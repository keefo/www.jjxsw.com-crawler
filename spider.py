import scrapy
import re
import json
import os.path

from scrapy.selector import Selector
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as sle
from scrapy.item import Item, Field
from os.path import exists

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['http://www.jjxsw.com/']
 
    if not os.path.exists("books"):
        os.makedirs("books")

    def parse(self, response):
        for link in response.xpath("//a[starts-with(@href, '/txt/')]"):
             name = link.xpath('text()').extract_first()
             url = link.xpath('@href').extract_first()
             if name is None or url is None:
                continue
             
             if not url.endswith(".htm"):
                yield response.follow(link, self.parse)
                continue

             path = "books/"+name+".txt"
             if not exists(path):
                 yield response.follow(link, self.parse_book_page, meta={'name': name})
             
    def parse_book_page(self, response):
        for link in response.xpath("//li[@class='downAddress_li']/a"):
            yield {'download': link.extract()}
            yield response.follow(link, self.parse_download_page, meta=response.meta)
            break
    
    def parse_download_page(self, response):
        for link in response.css("a.green"):
            title = link.xpath("text()").extract_first()
            if title.startswith( 'TXT电子书下载地' ):
                yield {'final_download': link.extract()}
                yield response.follow(link, self.save_text, meta=response.meta)                
                #return link
                break

    def save_text(self, response):
        path = response.url.split('/')[-1]
        extension = os.path.splitext(path)[1]

        self.logger.info('Saving Txt %s', path)
        name = "books/"+response.meta["name"]+extension
        with open(name, 'wb') as f:
            f.write(response.body)

