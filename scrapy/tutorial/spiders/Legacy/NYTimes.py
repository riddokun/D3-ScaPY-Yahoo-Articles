from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import BaseSpider
from selenium import webdriver
from scrapy.selector import HtmlXPathSelector, Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.dupefilter import RFPDupeFilter
from scrapy.utils.request import request_fingerprint
from tutorial.items import TutorialItem
from scrapy.http import Request
import time, datetime, csv, sys
import os.path
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import lxml.html

# Global variables
f = ""


class Tutorial1(CrawlSpider):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    fname = "C:\lol\NYTimes-" + current_time + ".csv"

    name = "ny"
    f = open(fname, 'wb')
    writer = csv.writer(f)
    writer.writerow(('Title', 'Sub-Headline', 'Source', 'Link Time', 'Article Time', 'Text', 'Link'))

    allowed_domains = ['http://www.nytimes.com/']
    start_urls = ["http://www.nytimes.com/pages/todayspaper/index.html"]

    def __init__(self):
        self.driver = webdriver.Chrome('C:\scrapy\chromedriver.exe')

    # Collects info and passes it to parse 2
    def parse(self, response):
        self.driver.get(response.url)
        try:
            hxs = Selector(response)
            titles = hxs.xpath('//h6')
            if last_title == "":
                exist_item = False
            elif last_title == "Title":
                exist_item = False
            else:
                exist_item = True

            for title in titles[::-1]:
                item = TutorialItem()
                item["Title"] = ''.join(title.xpath('a/@href/text()').extract())  # Gets the text
                if exist_item:
                    if ''.join(item["Title"]) == last_title:
                        exist_item = False
                else:
                    item["Source"] = ''.join(title.xpath('//div[@class=byline"]').extract())
                    item["Link"] = title.xpath("a/@href").extract()

                    url = ''.join(item['Link'])
                    req = Request(url, callback=self.parse_page2, dont_filter=True, priority=100)  # print url
                    req.meta['Title'] = ''.join(item['Title'])
                    req.meta['Source'] = ''.join(item['Source'])
                    req.meta['Link'] = ''.join(item['Link'])
                    yield req
                    sleep(2)
        except:
            exit()

    # In this class we will grab the previous data and store it in here with the remaining data that is being collected
    def parse_page2(self, response):  # data stored
        global writer
        ntime = 0.0
        millis = int(round(time.time() * 1000))  # Get the current time in milliseconds
        sel = HtmlXPathSelector(response)
        article = ''.join(sel.xpath('//div[@class="body yom-art-content clearfix"]/p/text()').extract())
        subheadline = ''.join(sel.xpath('//h2[@class="subheadline"]/text()').extract())
        str2 = ''.join(sel.xpath('//abbr/text()').extract())

        if "hour" in str2[1]:
            str3 = str2[1].split(" ")
            ntime += float(str3[0]) * 60
            if "minute" in str2[1]:
                ntime += float(str3[2])
        elif "minute" in str2[1]:
            str3 = str2[1].split(" ")
            ntime += float(str3[0])
        articletime = datetime.datetime.fromtimestamp((millis - ntime * 60 * 1000)/1000).strftime('%m-%d-%Y %H:%M:%S.%f')

        # Grabs the information from parse function
        title = response.meta['Title']
        source = response.meta['Source']
        link = response.meta['Link']

        # Stores everything in a CSV file
        Tutorial1.writer.writerow([title.encode("utf-8"), subheadline.encode("utf-8"), source.encode("utf-8"), linktime.encode("utf-8"),
                                  articletime.encode("utf-8"), article.encode("utf-8"), link.encode("utf-8")])

    def __exit__(self):
        global f
        f.close("\n")