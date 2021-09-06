""" A script to allocate all board_ids to a specific number of groups by their total pages and then use multiprocessing to call GamerCrawler.

The script will read 'target_board' collections to get all board ids and their total pages,
and then allocate all board ids into a specific number of groups, which is the same as the cpu counts in the machine,
and the sum of total pages in each group will be allocated as even as possible.
After the allocation, the script will use multiprocessing to execute GamerCrawler by passing the groups to them. 
"""


from multiprocessing import Process
import subprocess
import os
import sys
sys.path.append('..')
import logging 
from datetime import datetime 

from pymongo import MongoClient

from gamer_crawler.settings import DB_NAME
from gamer_crawler.config_logger import config_logger


logger = logging.getLogger(__name__)
logger = config_logger(logger)

def run(all_board_id, execution_time):
    """Execute a GamerCrawler spider to crawl multiple boards.
       
    Args:
        all_board_id [string]: use comma to join the board_id list
        execution_time [string]: execution time of this script in the format of %Y-%m-%d_%H:%M:%S
    """

    subprocess.check_call(f'scrapy crawl gamer -a all_board_id={all_board_id} -a execution_time={execution_time}', shell=True)

def allocate_board_groups(id_page_dic, group_num):
    """ Allocate total board_ids to a specific number of groups by their total pages as even as possible.

    Args:
        id_page_dic [dict]: a dictionary with all board ids as their keys, and all total pages respectively as their values.
        group_num [int]: the number of groups you want to allocate.

    Returns: A list of board_id list.
    """
    groups = []  # to store groups of board_ids
    id_page_dic = dict(sorted(id_page_dic.items(), key=lambda x: x[1], reverse=True))  # sort the id_page_dic by its value in the reverse order
    residual_group_count = group_num 

    stop = False  # A flag to stop the while loop
    while not stop:
        avg = sum(id_page_dic.values()) / residual_group_count  # The average total pages in each groups this round

        filter_out = [board_id for board_id in id_page_dic.keys() if id_page_dic[board_id] > avg]  # filter out all baords that exceed the average total pages
        if filter_out:
            for board_id in filter_out:
                groups.append([board_id])  # create a new group to store only one board, which exceeding the average total pages
                id_page_dic.pop(board_id)
                residual_group_count -= 1
        else:
            while residual_group_count > 1:
                round_group = []  # to store a group of board ids in this round
                round_sum = 0

                round_group.append(list(id_page_dic.keys())[0])  # take the first board_id, which has the most pages 
                round_sum += list(id_page_dic.values())[0]
                id_page_dic.pop(list(id_page_dic.keys())[0])
                while round_sum < avg:
                    round_group.append(list(id_page_dic.keys())[-1])  # take other board_id starting from the one which has the least pages 
                    round_sum += list(id_page_dic.values())[-1]
                    id_page_dic.pop(list(id_page_dic.keys())[-1])
                groups.append(round_group)  # create a new group to store round_group
                residual_group_count -= 1
            groups.append(list(id_page_dic.keys()))
            stop = True
    return groups


if __name__ == "__main__":
    
    execution_time = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')

    # store the board_id versus its total_page in a dictionary
    id_page_dic = dict()
    for doc in MongoClient(os.getenv('DB_URL'))[DB_NAME].target_board.find():
        id_page_dic[doc['board_id']] = doc['total_page']

    id_groups = allocate_board_groups(id_page_dic, os.cpu_count())

    # for each group of board_ids, create a process to run GamerCrawler
    processes = list()
    for id_group in id_groups:
        arg = ','.join(id_group)
        processes.append(Process(target=run, args=(arg,execution_time,)))

    for proc in processes:
        proc.start()

    for proc in processes:
        proc.join()

    logger.info('='*80)