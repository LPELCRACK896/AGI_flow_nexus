import scrapy

class ExcelReportSpider(scrapy.Spider):
    name = "excel_report_spider"
    allowed_domains = ["redmet.icc.org.gt"]
    start_urls = [
        'https://redmet.icc.org.gt/redmet/comparativas',
    ]

    def parse(self, response):
        file_name = response.url.split("/")[-1]
        
        self.save_file(response, file_name)

    def save_file(self, response, file_name):
        with open(file_name, 'wb') as f:
            f.write(response.body)
        self.log(f'Archivo guardado: {file_name}')
