# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SixMinuteEnglishPodcastSpiderItem(scrapy.Item):
    number = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    release_date = scrapy.Field()
    release_year = scrapy.Field()
    
    pdf_url = scrapy.Field()
    mp3_url = scrapy.Field()
    pdf_path = scrapy.Field()
    mp3_path = scrapy.Field()
    
