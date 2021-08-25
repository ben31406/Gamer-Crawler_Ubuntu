# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GamerCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    article_id = scrapy.Field()
    author_id = scrapy.Field()
    board_id = scrapy.Field()
    title = scrapy.Field()
    command_count = scrapy.Field()
    view_count = scrapy.Field()
    execution_time = scrapy.Field()
    crawling_time = scrapy.Field()


class TargetBoardItem(scrapy.Item):
    board_id = scrapy.Field()