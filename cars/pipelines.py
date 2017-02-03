# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from six.moves.urllib.parse import urlparse, parse_qsl
from scrapy.pipelines.files import FilesPipeline


class CarsPipeline(object):
    def process_item(self, item, spider):
        return item


class FileDownloadPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        parsed = dict(parse_qsl(urlparse(request.url).query))
        year = json.loads(parsed['get'])['sYear'][0]
        title = parsed['title'].lower().replace(' ', '_')
        return '{}_{}.csv'.format(title, year)
