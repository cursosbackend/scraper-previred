import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from previred_scraper.spiders.previred_spider import PreviredSpider
from previred_scraper.spiders.sii_utm_spider import SiiUtmSpider
from previred_scraper.pipelines import save_excel


def run_spiders():
    process = CrawlerProcess(get_project_settings())
    process.crawl(PreviredSpider)
    process.crawl(SiiUtmSpider)
    process.start()


def generate_dashboard():
    import subprocess
    subprocess.run([sys.executable, "generate_dashboard.py"], check=True)


if __name__ == "__main__":
    print("=" * 50)
    print("Iniciando scraping Previred + SII...")
    print("=" * 50)
    run_spiders()
    print("\n" + "=" * 50)
    print("Generando dashboard...")
    print("=" * 50)
    generate_dashboard()
    print("\n" + "=" * 50)
    print("Completado exitosamente.")
    print("=" * 50)
