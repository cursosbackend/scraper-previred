from scrapy import signals


class PreviredScraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_open, signal=signals.spider_open)
        return s

    def spider_open(self, spider):
        pass


class PreviredScraperDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_open, signal=signals.spider_open)
        return s

    def spider_open(self, spider):
        pass
