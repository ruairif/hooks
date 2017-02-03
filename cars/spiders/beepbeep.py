from six.moves.urllib.parse import urljoin
from scrapy import Spider, Request


class BeepBeepSpider(Spider):
    name = 'beepbeep.ie'
    BASE_URL = ('http://www.beepbeep.ie/stats?sYear%5B%5D={}&sYear%5B%5D=&s'
                'RegType=1&sMonth%5B%5D=&sMonth%5B%5D=&x=46&y=6').format

    def start_requests(self):
        for year in range(2007, 2017):
            yield Request(self.BASE_URL(year), meta={'year': year})

    def parse(self, response):
        return {
            'file_urls': [
                urljoin(response.url, link)
                for link in response.css('.exporttabs>a::attr(href)').extract()
                if 'excel' in link
            ]
        }
