__author__ = 'kreed25'

from scrapy.spider import Spider
from scrapy.selector import Selector

class MySpider(Spider):
    name = "google"
    allowed_domains = ["craigslist.org"]
    start_urls = [
        "http://sfbay.craigslist.org/npo/",
    ]

    def parse(self, response):
        for sel in response.xpath("//span[@class='pl']"):
            title = sel.xpath("a/text()").extract()
            link = sel.xpath("a/@href").extract()
            #time = sel.selector("/@datetime/title").extract()
            print title



        print "---------------------------"

        #for sel in response.xpath("//y"):
         #   title = sel.xpath("p/a/text()").extract()
        #    print title

        #filename = response.url.split("/")[-2]
        #with open(filename, 'wb') as f:
            #f.write(response.body)