from multiprocessing import Process
import subprocess
import os
import sys
sys.path.append('..')

from pymongo import MongoClient

from gamer_crawler.settings import DB_NAME


def run(all_board_id):
    # os.chdir(r'/app/')
    subprocess.check_call(f'scrapy crawl gamer -a all_board_id={all_board_id}', shell=True)




id_list = MongoClient(os.getenv('DB_URL'))[DB_NAME].target_board.distinct('board_id')
id_list = [str(i) for i in id_list]
if '60076' in id_list:
    id_list.remove('60076')
if '60030' in id_list:
    id_list.remove('60030')

processes = list()
# processes.append(Process(target=run, args=('60446',)))
# processes.append(Process(target=run, args=('39344',)))
processes.append(Process(target=run, args=('60076',)))
processes.append(Process(target=run, args=('60030',)))
arg1 = ','.join(id_list[:68])
processes.append(Process(target=run, args=(arg1,)))
arg2 = ','.join(id_list[68:136])
processes.append(Process(target=run, args=(arg2,)))
arg3 = ','.join(id_list[136:204])
processes.append(Process(target=run, args=(arg3,)))
arg4 = ','.join(id_list[204:272])
processes.append(Process(target=run, args=(arg4,)))
arg5 = ','.join(id_list[272:340])
processes.append(Process(target=run, args=(arg5,)))
arg6 = ','.join(id_list[340:])
processes.append(Process(target=run, args=(arg6,)))

from spiders.gamer_spider import GamerCrawler
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == "__main__":
    for process in processes:
        process.start()

    for process in processes:
        process.join()

    # process = CrawlerProcess(get_project_settings())
    # process.crawl(GamerCrawler, all_board_id='60076')
    # process.crawl(GamerCrawler, all_board_id='60030')
    # arg1 = ','.join(id_list[:68])
    # process.crawl(GamerCrawler, all_board_id=arg1)
    # arg2 = ','.join(id_list[68:136])
    # process.crawl(GamerCrawler, all_board_id=arg2)
    # arg3 = ','.join(id_list[136:204])
    # process.crawl(GamerCrawler, all_board_id=arg3)
    # arg4 = ','.join(id_list[204:272])
    # process.crawl(GamerCrawler, all_board_id=arg4)
    # arg5 = ','.join(id_list[272:340])
    # process.crawl(GamerCrawler, all_board_id=arg5)
    # arg6 = ','.join(id_list[340:])
    # process.crawl(GamerCrawler, all_board_id=arg6)
    # process.start()