import logging
from gamer_crawler.settings import HOT_VALUE
from gamer_crawler.items import TargetBoardItem
from gamer_crawler.items import GamerCrawlerItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import scrapy
from datetime import datetime
import json
import re
import os
import sys
sys.path.append('..')


class TargetBoardCrawler(scrapy.Spider):
    name = 'Target_board'
    domain_url = 'https://forum.gamer.com.tw/'

    blist_page = 1
    blist_base_url = '?page={}'     # 哈拉版列表url
    alist_base_url = 'B.php?bsn={}'  # 文章列表url
    start_urls = [domain_url + blist_base_url.format(blist_page)]

    def parse(self, response):
        reg = r'var _data = (\[.*\]),'
        data = re.search(reg, response.text).group(1)
        data = json.loads(data)
        for d in data:
            if int(d['hot']) >= HOT_VALUE:
                target_item = TargetBoardItem()
                target_item['board_id'] = d['bsn']
                yield target_item
            else:
                return None
        self.blist_page += 1
        yield scrapy.Request(self.domain_url + self.blist_base_url.format(self.blist_page), callback=self.parse)

    # def get_total_page(self, response):
    #     bid = response.url.split('bsn=')[1]
    #     total_page_xpath = '//div[@class="b-pager pager"][position()=1]//p[@class="BH-pagebtnA"]//a[position()=last()]//text()'
    #     total_page = response.xpath(total_page_xpath).get()
    #     target_item = TargetBoardItem()
    #     target_item['board_id'] = bid
    #     target_item['total_page'] = int(total_page)
    #     yield target_item


class GamerCrawler(CrawlSpider):
    name = 'gamer'
    execution_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

    def __init__(self, all_board_id, **kwargs):    
        self.all_board_id = all_board_id.split(',')
        url_temp = []
        for bid in self.all_board_id:
            url_temp.append(
                f'https://forum.gamer.com.tw/B.php?page=1&bsn={bid}')
        self.start_urls = url_temp.copy()
        self.rules = [
            Rule(LinkExtractor(allow=('B\.php\?page=.*&bsn=.*')),
                 callback='parse', follow=True)
        ]
        super().__init__(**kwargs)

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
