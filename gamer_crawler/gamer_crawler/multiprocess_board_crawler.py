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
    subprocess.check_call(f'scrapy crawl gamer -a all_board_id={all_board_id} -a execution_time={execution_time}', shell=True)

def allocate_board_groups(id_page_dic, group_num):
    '''
        allocate total board_ids to a specific number of groups
    '''
    groups = []
    id_page_dic = dict(sorted(id_page_dic.items(), key=lambda x: x[1], reverse=True))
    residual_group_count = group_num

    stop = False
    while not stop:
        avg = sum(id_page_dic.values()) / residual_group_count

        filter_out = [board_id for board_id in id_page_dic.keys() if id_page_dic[board_id] > avg]
        if filter_out:
            for board_id in filter_out:
                groups.append([board_id])
                id_page_dic.pop(board_id)
                residual_group_count -= 1
        else:
            while residual_group_count > 1:
                round_group = []
                round_sum = 0

                round_group.append(list(id_page_dic.keys())[0])
                round_sum += list(id_page_dic.values())[0]
                id_page_dic.pop(list(id_page_dic.keys())[0])
                while round_sum < avg:
                    round_group.append(list(id_page_dic.keys())[-1])
                    round_sum += list(id_page_dic.values())[-1]
                    id_page_dic.pop(list(id_page_dic.keys())[-1])
                groups.append(round_group)
                residual_group_count -= 1
            groups.append(list(id_page_dic.keys()))
            stop = True
    return groups


if __name__ == "__main__":
    
    execution_time = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')

    # store the board_id versus its total_page in a dictionary
    id_page_dic = dict()
    for doc in MongoClient(os.getenv('DB_URL')).gamer.target_board.find():
        id_page_dic[doc['board_id']] = doc['total_page']

    # use "id_page_dic" to allocate board_id
    id_groups = allocate_board_groups(id_page_dic, os.cpu_count())

    # for each group of board_ids, create a process to run gamer crawler
    processes = list()
    for id_group in id_groups:
        arg = ','.join(id_group)
        processes.append(Process(target=run, args=(arg,execution_time,)))

    for proc in processes:
        proc.start()

    for proc in processes:
        proc.join()

    logger.info('='*80)