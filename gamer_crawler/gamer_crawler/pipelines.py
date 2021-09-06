from itemadapter import ItemAdapter
import os
import sys
sys.path.append('..')
import logging 

from pymongo import MongoClient

from gamer_crawler.items import GamerCrawlerItem, TargetBoardItem
from gamer_crawler.settings import DB_NAME
from gamer_crawler.config_logger import config_logger


logger = logging.getLogger(__name__)
logger = config_logger(logger)

class GamerCrawlerPipeline:

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        # to get crawler stats
        return cls(crawler.stats)

    def open_spider(self, spider):
        self.client = MongoClient(os.getenv('DB_URL'))  # create MongoDB connection

    def process_item(self, item, spider):
        if isinstance(item, GamerCrawlerItem):
            self.tb = self.client[DB_NAME].gamer_info
            self.tb.insert_one(dict(item))
        elif isinstance(item, TargetBoardItem):
            self.tb = self.client[DB_NAME].target_board
            if not self.tb.find_one({"board_id": item['board_id']}):
                self.tb.insert_one(dict(item))
            else:
                self.tb.update_one({'board_id': item['board_id']}, {'$set': {'total_page': item['total_page']}})  # update the total page og the board
        return item

    def close_spider(self, spider):
        if spider.name == 'gamer':
            item_scraped_count = self.stats.get_stats()['item_scraped_count']  # get the total item scraped by the crawler
            logger.info('item_scraped_count for the spider starting at ' + spider.execution_time + ': ' + str(item_scraped_count))