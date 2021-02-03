# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exporters import JsonLinesItemExporter
from languages.items import LanguagesItem, TranslateItem
from typing import Dict, Tuple, IO
import os
import re


def open_file(filename: str, mode: str) -> IO:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    return open(filename, mode)


class LanguagesPipeline:
    lang_data_map: Dict[str, Tuple[str, JsonLinesItemExporter]] = {}
    trans_data_map: Dict[str, JsonLinesItemExporter] = {}

    def check_exporter(self, item):
        if isinstance(item, LanguagesItem):
            if item.spider not in self.lang_data_map:
                f = open_file(f'samples/{item.spider}-0xxx.json', 'wb')
                exporter = JsonLinesItemExporter(f)
                exporter.start_exporting()
                self.lang_data_map[item.spider] = ("0xxx", exporter)
                return exporter
            else:
                (pattern, exporter) = self.lang_data_map[item.spider]
                if (pattern == "0xxx" and item.id >= 1000)\
                        or (pattern != "0xxx" and not re.fullmatch(re.sub("x", "\\\\d", pattern), str(item.id))):
                    pattern = item.id // 1000
                    pattern = f'{pattern}xxx' if pattern > 0 else '0xxx'
                    exporter.finish_exporting()
                    f = open_file(f'samples/{item.spider}-{pattern}.json', 'wb')
                    exporter = JsonLinesItemExporter(f)
                    exporter.start_exporting()
                    self.lang_data_map[item.spider] = (pattern, exporter)
                return exporter
        elif isinstance(item, TranslateItem):
            if item.spider not in self.trans_data_map:
                f = open_file(f'translates/{item.spider}.json', 'wb')
                exporter = JsonLinesItemExporter(f)
                exporter.start_exporting()
                self.trans_data_map[item.spider] = exporter
            else:
                exporter = self.trans_data_map[item.spider]
            return exporter

    def process_item(self, item, _):
        exporter = self.check_exporter(item)
        if isinstance(item, LanguagesItem):
            print(f"export language item {item.id}")
        else:
            print(f"export translate item {item.ids}")
        exporter.export_item(item)
        return item
