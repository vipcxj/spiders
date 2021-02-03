import scrapy
from bs4 import BeautifulSoup
import os
import re

from languages.items import Source, LanguagesItem, TranslateItem

DIRECTORY_URL = 'https://www.en84.com/nonfiction/index.php?page='


def check_node(selector, cn) -> bool:
    style = selector.xpath("@style")
    font = "宋体" if cn else "Times New Roman"
    if style.re(f"font-family:\\s*{font}") is not None and not style.re(f"-font-family:\\s*{font}"):
        text = selector.xpath("./text()").get()
        return True if text and text.strip() else False
    return False


class En84Spider(scrapy.Spider):

    name = "en84"
    page = 1
    id_base = 0

    def start_requests(self):
        yield scrapy.Request(
            url=f'{DIRECTORY_URL}{self.page}',
            callback=self.parse_directory,
        )

    def parse(self, response, **kwargs):
        pass

    def parse_directory(self, response):
        for next_page in response.css("div.bm > div.bm_c.xld > dl > dt > a::attr(href)").getall():
            next_page = response.urljoin(next_page)
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_content,
            )
        page_num = response.css("div.pgs.cl a.last::text").re_first(r'[\d]+')
        if self.page < int(page_num):
            self.page += 1
            yield scrapy.Request(
                url=f'{DIRECTORY_URL}{self.page}',
                callback=self.parse_directory,
            )

    def parse_content(self, response):
        lst_item = None
        lst_used = False
        cur_item = None
        index = 0
        items = []
        for paragraph in response.xpath("//*[@id='article_content']//p"):
            b_soup = BeautifulSoup(paragraph.get(), "html.parser")
            text = re.sub("\\s+", " ", b_soup.get_text())
            if not text.strip():
                continue
            title = response.css("#ct > div.mn > div.bm.vw > div.h.hm > h1::text").get()
            en_span = check_node(paragraph.xpath(".//span[contains(@style, 'Times New Roman')]"), False)
            cn_span = check_node(paragraph.xpath(".//span[contains(@style, '宋体')]"), True)
            lang = 'en' if en_span and not cn_span else 'cn'
            self.id_base += 1
            cur_id = self.id_base
            cur_item = LanguagesItem(
                cur_id,
                content=text,
                lang=lang,
                source=Source(
                    url=response.url,
                    name=title,
                    keyword=[],
                    index=index,
                ),
                spider=self.name,
            )
            index += 1
            if lst_item is None:
                lst_item = cur_item
            elif lst_item.lang == cur_item.lang:
                lst_item.content += os.linesep + cur_item.content
            else:
                items.append(lst_item)
                if not lst_used:
                    trans_item = TranslateItem(
                        ids=[lst_item.id, cur_item.id] if lst_item.lang == 'cn' else [cur_item.id, lst_item.id],
                        spider=self.name,
                    )
                    items.append(trans_item)
                    lst_item = cur_item
                    lst_used = True
                else:
                    lst_item = cur_item
                    lst_used = False
        if cur_item is not None:
            items.append(cur_item)
        return items
