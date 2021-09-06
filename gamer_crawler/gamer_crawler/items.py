import scrapy


class GamerCrawlerItem(scrapy.Item):
    """field of gamer_info collection"""
    article_id = scrapy.Field()
    author_id = scrapy.Field()
    board_id = scrapy.Field()
    title = scrapy.Field()
    command_count = scrapy.Field()
    view_count = scrapy.Field()
    execution_time = scrapy.Field()
    crawling_time = scrapy.Field()


class TargetBoardItem(scrapy.Item):
    """field of target_board collection"""
    board_id = scrapy.Field()
    total_page = scrapy.Field()