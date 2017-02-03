import re

from collections import namedtuple
from xlrd import open_workbook
_IDENTIFIER_RE = re.compile('[^a-zA-Z0-9\s]')
_YEAR_RE = re.compile('([12][90][9012][0-9])')


class FileParser(object):
    def __init__(self, filename):
        self.rows = list(open_workbook(filename).sheets()[0].get_rows())

    def split(self):
        data, collection, title = [], None, ''
        for row in self.rows:
            types = [c.ctype for c in row]
            row_types_value = sum(types)
            if not row_types_value:
                continue
            if row_types_value == 1:
                title = ''.join(str(c.value) for c in row)
            elif all(t in (1, 0) for t in types):
                collection = Collection(title, [c.value for c in row])
                data.append(collection)
            else:
                collection.add(row)
        return data


class Collection(object):
    def __init__(self, title, headings):
        self.title = title.split('.')[0]
        self.headings = headings
        self.objects = []

    def add(self, object):
        self.objects.append([c.value for c in object])

    def __iter__(self):
        self._shift_headings()
        headings = [v if v else None for v in self.headings]
        title = self._build_title()
        T = namedtuple(title, filter(bool, headings))
        for obj in self.objects:
            yield T(*(o for h, o in zip(headings, obj) if h))

    def _shift_headings(self):
        headings = self.headings
        empty = [1 for _ in headings]
        for i, v in enumerate(empty):
            for row in self.objects:
                if row[i]:
                    break
            else:
                continue
            empty[i] = 0
        for i, v in enumerate(empty):
            if not v:
                continue
            if headings[i]:
                if not headings[i + 1]:
                    headings[i], headings[i + 1] = headings[i + 1], headings[i]
                if not headings[i - 1]:
                    headings[i], headings[i - 1] = headings[i - 1], headings[i]
        for i, head in enumerate(headings):
            if head and head[0].isdigit():
                split = head.split(' ', 1)
                num = split.pop(0)
                split.append(num)
                head = ' '.join(split)
            head = head.replace('%', ' pc ').replace('/', ' or ')
            head = _IDENTIFIER_RE.sub('', head)
            headings[i] = head.replace(' ', '_').replace('__', '_').strip('_')

    def _build_title(self):
        title = self.title.replace(' ', '')
        matches = [_YEAR_RE.search(h) for h in self.headings]
        years = []
        if ('todate' in title.lower() and any(matches)):
            for i, match in enumerate(matches):
                if not match:
                    continue
                year = match.group()
                years.append(int(year))
                heading = self.headings[i]
                self.headings[i] = heading.replace(year, '').strip('_')
            year = max(years)
            title = '{}{}'.format(title.replace('todate', ''), year)
        return title
