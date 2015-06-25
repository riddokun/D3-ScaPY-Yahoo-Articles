# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

#import scrapy
from scrapy.item import Item, Field


class TutorialItem(Item):
    Source = Field()
    LinkTime = Field()
    Title = Field()
    Link = Field()
    Author = Field()
    Article = Field()


class ArticleItem(Item):
    Title = Field()
