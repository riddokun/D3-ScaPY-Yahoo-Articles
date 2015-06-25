from scrapy.contrib.spiders import CrawlSpider
from selenium import webdriver
from scrapy.selector import HtmlXPathSelector, Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.dupefilter import RFPDupeFilter
from scrapy.utils.request import request_fingerprint
from scrapy.http import Request
import time, datetime, csv, sys
import os.path
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class ArticleTime(CrawlSpider):
    name = "article"
    allowed_domains = ['finance.yahoo.com/news']
    start_urls = ["http://finance.yahoo.com/news/provider-ap"]

    def __init__(self):
        self.driver = webdriver.Firefox()

    def parse(self, response):
        millis = int(round(time.time() * 1000))
        f = open("C:\data\BusinessWire.csv", 'rb')
        g = open("C:\data\BusinessWire Test.csv", 'wb')
        reader = csv.reader(f)
        writer = csv.writer(g)

        headers = None
        for row in reader:
            if not headers:
                #sprint "read header"
                headers = row
                #print headers
                writer.writerow(row)
            else:
                self.driver.get(row[6])
                hxs = HtmlXPathSelector(text=self.driver.page_source)
                print row[6]
                titles = hxs.xpath('//div[@class="credit-text"]')
                for title in titles:
                    str2 = ''.join(title.xpath('//abbr/text()').extract())
                    if "ago" in str2:
                        if "hour" in str2:
                            str3 = str2.split(" ")
                            mtime += float(str3[0]) * 60
                            if "minute" in str2:
                                mtime += float(str3[2])
                        elif "minute" in str2:
                            str3 = str2.split(" ")
                            mtime += float(str3[0])
                        articletime = datetime.datetime.fromtimestamp((millis - mtime * 60 * 1000)/1000).strftime('%m-%d-%Y %H:%M')
                        print articletime
                        row[4] = articletime
                    else:
                        str3 = str2.split(", ")
                        str4 = str3[1].split(" ")
                        str5 = str4[1].split(":")
                        hm = str4[1]
                        if str4[2] == "PM":
                            hour = int(str5[0])
                            if hour == 12:
                                hm = str(hour) + ":" + str5[1]
                            else:
                                hm = str(hour + 12) + ":" + str5[1]
                        else:
                            hour = int(str5[0])
                            if hour == 12:
                                hm = str(hour - 12) + ":" + str5[1]
                            else:
                                hm = str(hour) + ":" + str5[1]
                        tmp_s_date = str3[0] + ' ' + str4[0] + ' ' + hm
                        stime = time.strptime(tmp_s_date, "%B %d %Y %H:%M")  # string does not contain "hours" or "minutes" so need to check this is before or after the start date
                        mtime = time.mktime(stime)
                        articletime = datetime.datetime.fromtimestamp(mtime).strftime('%m-%d-%Y %H:%M')
                        print articletime
                        row[4] = ''.join(articletime)

                    writer.writerow(row)

    def __exit__(self):
        global f
        f.close("\n")
        g.close("\n")