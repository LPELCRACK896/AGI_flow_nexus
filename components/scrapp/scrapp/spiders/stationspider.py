from scrapy.http import FormRequest, Request
from dotenv import dotenv_values
from icc_scraper.utils import *
from icc_scraper.items import StationItem, WeatherStationItem
import scrapy
import json

config = dotenv_values(".env") 
ICC_USER =config['ICC_USER']
ICC_PASSWORD = config['ICC_PASSWORD']

class StationSpider(scrapy.Spider):
    
    name = "stationspider"
    allowed_domains = ["redmet.icc.org.gt"]
    start_urls = ["https://redmet.icc.org.gt/redmet/mapa"]
    
    def __init__(self, station_id = None, *args, **kwargs):
        self.station_id = station_id 
        super(StationSpider, self).__init__(*args, **kwargs)



    def parse(self, response):

        input_hidden_token = response.xpath('//input[@type="hidden" and @name="_token"]').attrib['value']
        return FormRequest.from_response(
            response,
            formdata={'_token': input_hidden_token,
                      'email': ICC_USER,
                      'password': ICC_PASSWORD},
            callback=self.after_login)
        
    def after_login(self, response):
        if self.station_id is None:  # GETS ALL 
            reports_url = "https://redmet.icc.org.gt/redmet/comparativas"
            yield response.follow(reports_url, callback=self.parse_existing_stations_ids)
        else:  # GETS ONLY GIVEN 
            get_station_url = f"https://redmet.icc.org.gt/redmet/mapa/{self.station_id}"
            yield scrapy.Request(get_station_url, callback=self.parse_station_data)

    def parse_existing_stations_ids(self, response):
        stations = response.xpath("//select[@id='fincas']//option")
        station_ids = [option.xpath("@value").get() for option in stations]

        for s_id in station_ids:
            get_station_url = f"https://redmet.icc.org.gt/redmet/mapa/{s_id}"
            yield scrapy.Request(get_station_url, callback=self.parse_station_data)

    def parse_station_data(self, response):

        {
            'nombre': 'Toro Blanco NI', 
            'color': None,
            'estacionid': 64,
            'latitud': 12.68,
            'longitud': -87.2,
            'altitud': 0,
            'estrato': 'Litoral',
            'fecha': '14-08 18:15',
            'lecturas': {
                'temperatura': '24.80', 
                'radiacion': '0.00', 
                'humedad_relativa': '95.00', 
                'precipitacion': '0.00', 
                'velocidad_viento': '1.10'
                }
            }
        data = json.loads(response.body)
        yield StationItem(
            station_id = data["estacionid"], 
            name = data["nombre"],
            latitude = data["latitud"],
            longitude = data["longitud"],
            altitude = data["altitud"],
            stratum = data["estrato"])
        
        yield WeatherStationItem(
            station_id = data["estacionid"],
            date_time = data["fecha"],
            temperature = data["lecturas"]["temperatura"],
            radiation = data["lecturas"]["radiacion"],
            relative_humidity = data["lecturas"]["humedad_relativa"],
            precipitation = data["lecturas"]["precipitacion"],
            wind_speed = data["lecturas"]["velocidad_viento"]
        )

        self.logger.info(data)