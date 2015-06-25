from scrapy.contrib.spiders import CrawlSpider
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

# Global variables
f = ""


class Tutorial1(CrawlSpider):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    fname = "C:\lol\News-" + current_time + ".csv"

    name = "dailynews"
    f = open(fname, 'wb')
    writer = csv.writer(f)
    writer.writerow(('Title', 'Sub-Headline', 'Source', 'Link Time', 'Article Time', 'Text', 'Link'))

    allowed_domains = ['finance.yahoo.com/news']
    start_urls = ["http://finance.yahoo.com/news/provider-cnnmoney"]

    def __init__(self):
        self.driver = webdriver.Chrome('C:\scrapy\chromedriver.exe')
        # self.driver = webdriver.FireFox()

    # Collects info and passes it to parse 2
    def parse(self, response):
        millis = int(round(time.time() * 1000))  # Get the current time in milliseconds
        providers = ["cnnmoney", "ap", "the-atlantic", "accesswire", "bloomberg", "bankrate", "benzinga", "businessinsider", "businesswire", "capitalcube",
                     "cbsmoneywatch", "cnbc", "cnwgroup", "consumer-reports", "credit", "credit-cards", "dailyfx", "dailyworth", "engadget", "entrepreneur",
                     "etf-trends", "etfguide", "forbes", "fortune", "foxbusiness", "thefiscaltimes", "globenewswire", "gurufocus", "investors-business-daily",
                     "market-realist", "marketwire", "money", "moneytalksnews", "mrtopstep", "optionmonster", "paidcontent", "prnewswire", "reuters"]
        list_all = []
        for provider in providers:
            self.driver.get("http://finance.yahoo.com/news/provider-" + provider)
            try:
                next = self.driver.find_element_by_xpath('//a[@class="more more-inline"]')
                loop = True
                while loop:
                    hxs = HtmlXPathSelector(text=self.driver.page_source)
                    titles = hxs.xpath('//div[@class="txt"]')
                    for title in titles[::-1]:
                        item = TutorialItem()
                        item["Title"] = ''.join(title.xpath("a/text()").extract())
                        str1 = ''.join(title.xpath('cite/text()').extract())  # Splits the text

                        str2 = str1.split(" - ")  # gets everything after this symbol
                        item["Source"] = str2[0]  # Prints the text from 0 to the character "-"

                        if "ago" in str2[1]:
                            list_all.append(hxs)
                            break
                        else:
                            list_all.append(hxs)
                            loop = False
                            break
                    next.click()
                    # make sure the page loading is done, currently 10 sec
                    sleep(3)
            except:
                hxs = HtmlXPathSelector(text=self.driver.page_source)
                list_all.append(hxs)

        for hxs in list_all:
            titles = hxs.xpath('//div[@class="txt"]')
            print "start collecting"
            for title in titles:
                item = TutorialItem()
                item["Title"] = ''.join(title.xpath("a/text()").extract())
                str1 = ''.join(title.xpath('cite/text()').extract())  # Splits the text
                str2 = str1.split(" - ")  # gets everything after this symbol
                item["Source"] = str2[0]  # Prints the text from 0 to the character "-"
                mtime = 0.0
                if "ago" in str2[1]:
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

                    item["Link"] = title.xpath("a/@href").extract()
                    url = ""
                    if "@" in str1:
                        url = ''.join(item['Link'])
                        req = Request(url, callback=self.parse_provider, dont_filter=True, priority=100)  # print url
                    else:
                        url = "http://finance.yahoo.com" + ''.join(item['Link'])
                        req = Request(url, callback=self.parse_yahoo, dont_filter=True, priority=100)  # print url

                    req.meta['Title'] = ''.join(item['Title'])
                    req.meta['Source'] = ''.join(item['Source'])
                    req.meta['LinkTime'] = ''.join(item["LinkTime"])
                    req.meta['Link'] = ''.join(item['Link'])
                    req.meta['current_time'] = millis
                    yield req
                    sleep(3)
                else:
                    break

    def parse_provider(self, response):  # data stored
        global writer
        sel = HtmlXPathSelector(response)

        # Grabs the information from parse function
        title = response.meta['Title']
        linktime = response.meta['LinkTime']
        source = response.meta['Source']
        link = response.meta['Link']

        if "CNN" in source:
            article = ''.join(sel.xpath('//p/text()').extract())
            subheadline = ''.join(sel.xpath('//h2/text()').extract())
            articletime = ''.join(sel.xpath('//span[@class="cnnDateStamp"]/text()').extract())
        elif "Bloomberg" in source:
            article = ''.join(sel.xpath('//section[@class="article-body"]/p/text()').extract())
            subheadline = " "
            articletime = ''.join(sel.xpath('//time/text()').extract())
        elif "BusinessWeek" in source:  # Remember it goes to bloomberg sites
            article = ''.join(sel.xpath('//section[@class="article-body"]/p/text()').extract())
            subheadline = " "
            articletime = ''.join(sel.xpath('//time/text()').extract())
        elif "Los Angeles Times" in source:
            article = ''.join(sel.xpath('//div[@class="trb_article_page"]/p/text()').extract())
            subheadline = " "
            articletime = ''.join(sel.xpath('//time[@class="trb_article_dateline_time"]/@data-datetime-month').extract()) + ' ' + ''.join(sel.xpath('//time[@class="trb_article_dateline_time"]/@data-datetime-day').extract()) + ' ' + ''.join(sel.xpath('//time[@class="trb_article_dateline_time"]/@data-datetime-fullclock').extract())
        elif "Forbes" in source:
            article = ''.join(sel.xpath('//p/text()').extract())
            subheadline = ''.join(sel.xpath('//h5[@itemprop="articleSelection"]/text()').extract())
            articletime = ''.join(sel.xpath('//time/text()').extract())
        elif "Money" in source:
            article = ''.join(sel.xpath('//section[@class="article-body"]/p/text()').extract())
            subheadline = ''.join(sel.xpath('//h2[@class="article-excerpt"]/a/text()').extract())
            articletime = ''.join(sel.xpath('//time[@class="publish-date"]/@datetime').extract())
        elif "Capital Cube" in source:
            article = ''.join(sel.xpath('//p/text()').extract())
            subheadline = ''.join(sel.xpath('//h5[@itemprop="articleSelection"]/text()').extract())
            articletime = ''.join(sel.xpath('//div[@class="entry-byline"]/abbr/text()').extract())
        elif "CNBC" in source:
            article = ''.join(sel.xpath('//div[@class="group"]/p/text()').extract())
            subheadline = ''.join(sel.xpath('//h2/text()').extract())
            articletime = ''.join(sel.xpath('//time[@class="publish-date"]/@datetime').extract())
        elif "Engadget" in source:
            article = ''.join(sel.xpath('//div[@class="article-content"]/p/text()').extract())
            subheadline = ''.join(sel.xpath('//h5[@itemprop="articleSelection"]/text()').extract())
            articletime = ''.join(sel.xpath('//span[@class="timeago"]/@datetime').extract())
        elif "Fortune" in source:
            article = ''.join(sel.xpath('//p/text()').extract())
            subheadline = ''.join(sel.xpath('//h2/text()').extract())
            articletime = ''.join(sel.xpath('//div[@class="article-byline"]/time/text()').extract())
        elif "Fox Business" in source:
            article = ''.join(sel.xpath('//div[@class="article-text"]//p/text()').extract())
            subheadline = ''.join(sel.xpath('//h5[@itemprop="articleSelection"]/text()').extract())
            articletime = ''.join(sel.xpath('//time/text()').extract())
        elif "Gigaom" in source:
            article = ''.join(sel.xpath('//p/text()').extract())
            subheadline = " "
            articletime = ''.join(sel.xpath('//time[@class="time published"]/text()').extract())
        elif "Investor's Business Daily" in source: #Check this one
            article = ''.join(sel.xpath('//p/text()').extract())
            subheadline = " "

            str = ''.join(sel.xpath('//span[@itemprop="printEdition"]/text()').extract())  # Splits the text
            strtime = ''.join(sel.xpath('//span[@itemprop="datePublished"]/text()').extract())

            str2 = str.split(", ")  # gets everything after this symbol

            if "2015" in str2[1]:
                str3 = str2[1].split(" ")
                mtime = str3[0] + " " + str3[1] + " " + str3[2]
            if "ET" in strtime[0]:
                str4 = strtime[0].split(" ")
                mtime2 = str4[0] + " " + str4[1]
            articletime = mtime + " " + mtime2  # subtracts the current time from the time of the article

        # Stores everything in a CSV file
        Tutorial1.writer.writerow([title.encode("utf-8"), subheadline.encode("utf-8"), source.encode("utf-8"), linktime.encode("utf-8"),
                                  articletime.encode("utf-8"), article.encode("utf-8"), link.encode("utf-8")])

    # Standard for most sites
    def parse_yahoo(self, response):  # data stored
        ntime = 0.0
        millis = response.meta['current_time']  # int(round(time.time() * 1000))  # Get the current time in milliseconds
        sel = HtmlXPathSelector(response)
        article = ''.join(sel.xpath('//div[@class="body yom-art-content clearfix"]/p/text()').extract())
        subheadline = ''.join(sel.xpath('//h2[@class="subheadline"]/text()').extract())
        str2 = ''.join(sel.xpath('//abbr/text()').extract())

        if "hour" in str2:
            str3 = str2.split(" ")
            ntime += float(str3[0]) * 60
            if "minute" in str2:
                ntime += float(str3[2])
            elif "minute" in str2:
                str3 = str2.split(" ")
                ntime += float(str3[0])
        articletime = datetime.datetime.fromtimestamp((millis - ntime * 60 * 1000)/1000).strftime('%m-%d-%Y %H:%M:%S.%f')

        # Grabs the information from parse function
        title = response.meta['Title']
        linktime = response.meta['LinkTime']
        source = response.meta['Source']
        link = "http://finance.yahoo.com" + response.meta['Link']

        # Stores everything in a CSV file
        Tutorial1.writer.writerow([title.encode("utf-8"), subheadline.encode("utf-8"), source.encode("utf-8"), linktime.encode("utf-8"),
                                  articletime.encode("utf-8"), article.encode("utf-8"), link.encode("utf-8")])

    def __exit__(self):
        global f
        f.close("\n")
