import scrapy
import os.path

from os.path import exists

class JJSpider(scrapy.Spider):
    name = 'jjspider'
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
            yield response.follow(link, self.parse_download_page, meta=response.meta)
            break
    
    def parse_download_page(self, response):
        for link in response.css("a.green"):
            title = link.xpath("text()").extract_first()
            if title.startswith( 'TXT电子书下载地' ):
                yield {'download_link': link.extract()}
                yield response.follow(link, self.save_text, meta=response.meta)                
                break

    def save_text(self, response):
        path = response.url.split('/')[-1]
        extension = os.path.splitext(path)[1]

        self.logger.info('Saving Txt %s', path)
        name = "books/"+response.meta["name"]+extension
        with open(name, 'wb') as f:
            f.write(response.body)

