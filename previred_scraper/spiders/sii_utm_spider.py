import scrapy

from previred_scraper.items import UTMItem


class SiiUtmSpider(scrapy.Spider):
    name = "sii_utm"
    start_urls = ["https://www.sii.cl/valores_y_fechas/utm/utm2026.htm"]

    def parse(self, response):
        rows = response.xpath("//table[@id='table_export']//tbody/tr")
        for tr in rows:
            tds = tr.xpath("./td")
            th = tr.xpath("./th")
            mes = th.xpath("normalize-space(text())").get() if th else None
            if not mes:
                continue
            item = UTMItem()
            item["mes"] = mes.strip() if mes else None
            item["utm"] = self._clean(tds[0].xpath("text()").get()) if len(tds) > 0 else None
            item["uta"] = self._clean(tds[1].xpath("text()").get()) if len(tds) > 1 else None
            item["ipc"] = self._clean(tds[2].xpath("normalize-space(text())").get()) if len(tds) > 2 else None
            item["var_mensual"] = self._clean(tds[3].xpath("normalize-space(text())").get()) if len(tds) > 3 else None
            item["var_acumulada"] = self._clean(tds[4].xpath("normalize-space(text())").get()) if len(tds) > 4 else None
            item["var_anual"] = self._clean(tds[5].xpath("normalize-space(text())").get()) if len(tds) > 5 else None
            yield item

    def _clean(self, val):
        if val is None:
            return None
        val = val.strip().replace("\xa0", " ")
        return val if val else None
