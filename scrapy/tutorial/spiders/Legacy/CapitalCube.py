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

# Global variables
f = ""


class CapitalCube(CrawlSpider):
    global last_title
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    current_hour = time.strftime("%X").split(":")[0]
    print current_hour
    fname = "C:\lol\CapitalCube-" + current_time + ".csv"
    previous_time = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime("%Y-%m-%d")

    #isaac
    #set start and end dates (Are they milliseconds?)
    #for now we set these manually here but it would be better to asign these by passing arguments.
    #this name also needs to be assigned by arguments...
    name = "cube"

    f = open(fname, 'wb')
    writer = csv.writer(f)
    writer.writerow(('Title', 'Sub-Headline', 'Source', 'Link Time', 'Article Time', 'Text', 'Link'))

    allowed_domains = ['finance.yahoo.com/news']
    start_urls = ["http://finance.yahoo.com/news/provider-capitalcube/"]

    def __init__(self):
        self.driver = webdriver.Firefox()

    # Collects info and passes it to parse 2
    def parse(self, response):
        millis = int(round(time.time() * 1000))  # Get the current time in milliseconds
        self.driver.get(response.url)
        next = self.driver.find_element_by_xpath('//a[@class="more more-inline"]')
        arry = []
        arry_hxs = []
        loop = True
        while loop:
            hxs = HtmlXPathSelector(text=self.driver.page_source)
            titles = hxs.xpath('//div[@class="txt"]')
            for title in titles[::-1]:
                item = TutorialItem()
                item["Title"] = ''.join(title.xpath("a/text()").extract())
                #print item["Title"].encode("utf-8")
                #this only check "minute ago...." not actual date
                #but we need to check Feb XX
                str1= ''.join(title.xpath('cite/text()').extract())  # Splits the text

                str2 = str1.split(" - ")  # gets everything after this symbol
                item["Source"] = str2[0]  # Prints the text from 0 to the character "-"

                mtime = 0.0
                if "ago" in str2[1]:
                    arry_hxs.append(hxs)
                    break
                else:
                    arry_hxs.append(hxs)
                    loop = False
                    break
            next.click()
            # make sure the page loading is done, currently 10 sec
            sleep(10)

        for articles in arry_hxs:
            tmp = []
            titles = articles.xpath('//div[@class="txt"]')
            print "start collecting"
            for title in titles:
                item = TutorialItem()
                item["Title"] = ''.join(title.xpath("a/text()").extract())
                #print item["Title"].encode("utf-8")
                str1 = ''.join(title.xpath('cite/text()').extract())  # Splits the text
                str2 = str1.split(" - ")  # gets everything after this symbol
                item["Source"] = str2[0]  # Prints the text from 0 to the character "-"
            #split string by month day year and others
                mtime = 0.0
                if "hour" in str2[1]:
                    str3 = str2[1].split(" ")
                    mtime += float(str3[0]) * 60
                    if "minute" in str2[1]:
                        mtime += float(str3[2])
                elif "minute" in str2[1]:
                    str3 = str2[1].split(" ")
                    mtime += float(str3[0])
                else:
                    exit(0)  # string does not contain "hours" or "minutes"
                item["LinkTime"] = datetime.datetime.fromtimestamp((millis - mtime * 60 * 1000)/1000).strftime('%m-%d-%Y %H:%M:%S.%f')  # subtracts the current time from the time of the article
                 #item["LinkTime"] = str2[1]  # subtracts the current time from the time of the article
                item["Link"] = title.xpath("a/@href").extract()
                if not ''.join(item['Link']) in arry:
                    tmp.append(''.join(item['Link']))
                url = "http://finance.yahoo.com" + ''.join(item['Link'])
                req = Request(url, callback=self.parse_page2, dont_filter=True, priority=100)  # print url
                req.meta['Title'] = ''.join(item['Title'])
                req.meta['Source'] = ''.join(item['Source'])
                req.meta['LinkTime'] = ''.join(item["LinkTime"])
                req.meta['Link'] = ''.join(item['Link'])
                yield req
                sleep(3)
            arry = tmp

    # In this class we will grab the previous data and store it in here with the remaining data that is being collected
    def parse_CapitalCube(self, response):  # data stored
        global writer
        sel = HtmlXPathSelector(response)
        article = ''.join(sel.xpath('//p/text()').extract())
        subheadline = ''.join(sel.xpath('//h5[@itemprop="articleSelection"]/text()').extract())
        articletime = ''.join(sel.xpath('//div[@class="entry-byline"]/abbr/text()').extract())

        # Grabs the information from parse function
        title = response.meta['Title']
        linktime = response.meta['LinkTime']
        source = response.meta['Source']
        link = response.meta['Link']

        # Stores everything in a CSV file
        CapitalCube.writer.writerow([title.encode("utf-8"), subheadline.encode("utf-8"), source.encode("utf-8"), linktime.encode("utf-8"),
                                  articletime.encode("utf-8"), article.encode("utf-8"), link.encode("utf-8")])

    def __exit__(self):
        global f
        f.close("\n")
