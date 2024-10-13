# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StationItem(scrapy.Item):
    station_id = scrapy.Field()
    name = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    altitude = scrapy.Field()
    stratum = scrapy.Field()


class WeatherStationItem(scrapy.Item):
    station_id = scrapy.Field()
    date_time = scrapy.Field()
    temperature = scrapy.Field()
    radiation = scrapy.Field()
    relative_humidity = scrapy.Field()
    precipitation = scrapy.Field()
    wind_speed = scrapy.Field()


class BasicStationItem(scrapy.Item):
    label = scrapy.Field()
    value = scrapy.Field()


class VariableItem(scrapy.Item):
    label = scrapy.Field()
    value = scrapy.Field()


class GroupItem(scrapy.Item):
    label = scrapy.Field()
    value = scrapy.Field()


class IccScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
