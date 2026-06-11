import os

BOT_NAME = "previred_scraper"

SPIDER_MODULES = ["previred_scraper.spiders"]
NEWSPIDER_MODULE = "previred_scraper.spiders"

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1

ITEM_PIPELINES = {
    "previred_scraper.pipelines.PdfsPipeline": 200,
    "previred_scraper.pipelines.ExcelPipeline": 300,
}

FILES_STORE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdfs")
MEDIA_ALLOW_REDIRECTS = True

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
