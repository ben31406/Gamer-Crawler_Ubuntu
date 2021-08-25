# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import sys
sys.path.append('..')

from pymongo import MongoClient

from gamer_crawler.items import GamerCrawlerItem, TargetBoardItem
from gamer_crawler.settings import DB_NAME



class GamerCrawlerPipeline:

    # def __init__(self, stats):
    #     self.stats = stats

    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.stats)


    def open_spider(self, spider):
        self.client = MongoClient(os.getenv('DB_URL'))

    def process_item(self, item, spider):
        if isinstance(item, GamerCrawlerItem):
            self.tb = self.client[DB_NAME].gamer_info
            self.tb.insert_one(dict(item))
        elif isinstance(item, TargetBoardItem):
            self.tb = self.client[DB_NAME].target_board
            if not self.tb.find_one({"board_id": item['board_id']}):
                self.tb.insert_one(dict(item))
        return item

    # def close_spider(self, spider):
    #     tt = self.stats.get_stats()['item_scraped_count']
    #     print('total item count:'+str(tt))
    #     print('name',spider.name)