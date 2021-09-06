from datetime import datetime
import json
import re
import os
import sys
sys.path.append('..')

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import scrapy

from gamer_crawler.settings import HOT_VALUE
from gamer_crawler.items import TargetBoardItem
from gamer_crawler.items import GamerCrawlerItem


class TargetBoardCrawler(scrapy.Spider):
    """A crawler to crawl all boards whose hot value >= HOT_VALUE
    
    This crawler will crawl all baord_ids and their total_page, and then store into MongoDB collection 'target_board'
    """

    name = 'Target_board'
    domain_url = 'https://forum.gamer.com.tw/'

    blist_page = 1
    blist_base_url = '?page={}'     # 哈拉版列表url
    alist_base_url = 'B.php?page=1&bsn={}'  # 文章列表url
    start_urls = [domain_url + blist_base_url.format(blist_page)]

    def parse(self, response):
        reg = r'var _data = (\[.*\]),'
        data = re.search(reg, response.text).group(1)
        data = json.loads(data)
        for d in data:
            if int(d['hot']) >= HOT_VALUE:
                bsn = d['bsn']
                yield scrapy.Request(self.domain_url + self.alist_base_url.format(bsn), callback=self.get_total_page)  # crawl into article list url of the board
            else:
                return None  # stop the crawler while the hot value less than the HOT_VALUE
        self.blist_page += 1
        yield scrapy.Request(self.domain_url + self.blist_base_url.format(self.blist_page), callback=self.parse)  # crawl next page

    def get_total_page(self, response):
        """the function will get the total page number of the board and then yield the TargetBoardItem to store into MongoDB"""
        bid = response.url.split('bsn=')[1]
        total_page_xpath = '//div[@class="b-pager pager"][position()=1]//p[@class="BH-pagebtnA"]//a[position()=last()]//text()'
        total_page = response.xpath(total_page_xpath).get()
        target_item = TargetBoardItem()
        target_item['board_id'] = bid
        target_item['total_page'] = int(total_page)
        yield target_item


class GamerCrawler(CrawlSpider):
    """A crawler to crawl all article information of some target boards.
    
    Given some board ids, the crawler will crawl over those boards to get all articles' information

    Args:
         all_board_id [string]: A string which derived from a list of all target boards' board_id, join by comma
         execution_time [string]: A time string, which represents the starting time of the multiprocessing
    """
    
    name = 'gamer'

    def __init__(self, all_board_id, execution_time, **kwargs):    
        self.all_board_id = all_board_id.split(',')
        self.execution_time = execution_time

        url_temp = []
        for bid in self.all_board_id:
            url_temp.append(
                f'https://forum.gamer.com.tw/B.php?page=1&bsn={bid}')  # to generate start_urls, which is the set of article_list_urls with the page 1
        self.start_urls = url_temp.copy()
        self.rules = [
            Rule(LinkExtractor(allow=('B\.php\?page=([2-9]|[0-9]{2,})&?bsn=\d+$')),
                 callback='parse', follow=True)
        ]   # the rule accept all pages without page 1, since the parse_start_url will parse the first page
        super().__init__(**kwargs)

    def parse_start_url(self, response):
        """this method allow the crawler parse the start url, otherwise, it won't parse it"""
        return self.parse(response)

    def parse(self, response):
        title_xpath = '//tr[@class="b-list__row b-list-item b-imglist-item"]//div[@class="b-list__tile"]/p/text()'
        title_list = response.xpath(title_xpath).getall()

        url_xpath = '//tr[@class="b-list__row b-list-item b-imglist-item"]//div[@class="b-list__tile"]/p/@href'
        article_url_list = response.xpath(url_xpath).getall()
        board_id_list = [self.get_id_from_url(u)[0] for u in article_url_list]
        article_id_list = [self.get_id_from_url(
            u)[1] for u in article_url_list]

        command_count_xpath = '//tr[@class="b-list__row b-list-item b-imglist-item"]//td[@class="b-list__count"]//span[position()=1]/@title'
        command_count_list = response.xpath(command_count_xpath).getall()
        command_count_list = list(
            map(lambda x: int(x.replace('互動：', '').replace(',', '')), command_count_list))

        view_count_xpath = '//tr[@class="b-list__row b-list-item b-imglist-item"]//td[@class="b-list__count"]//span[position()=2]/@title'
        view_count_list = response.xpath(view_count_xpath).getall()
        view_count_list = list(
            map(lambda x: int(x.replace('人氣：', '').replace(',', '')), view_count_list))

        author_id_xpath = '//tr[@class="b-list__row b-list-item b-imglist-item"]//td[@class="b-list__count"]//p[@class="b-list__count__user"]/a/text()'
        author_id_list = response.xpath(author_id_xpath).getall()

        for article_id, author_id, board_id, title, command_count, view_count in zip(article_id_list, author_id_list,
                                                                                     board_id_list,
                                                                                     title_list, command_count_list,
                                                                                     view_count_list):
            gamer_item = GamerCrawlerItem()
            gamer_item['article_id'] = article_id
            gamer_item['author_id'] = author_id
            gamer_item['board_id'] = board_id
            gamer_item['title'] = title
            gamer_item['command_count'] = command_count
            gamer_item['view_count'] = view_count
            gamer_item['execution_time'] = self.execution_time
            gamer_item['crawling_time'] = datetime.strftime(
                datetime.now(), '%Y-%m-%d %H:%M:%S')
            yield gamer_item

    @staticmethod
    def get_id_from_url(url):
        # output: board_id and article_id
        regex_str = r'C\.php\?bsn=(\d+)&snA=(\d+)'
        board_id = re.search(regex_str, url).group(1)
        article_id = re.search(regex_str, url).group(2)
        return board_id, article_id
