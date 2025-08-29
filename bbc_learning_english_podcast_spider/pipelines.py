# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# Standard library imports
from pathlib import Path

# Third-party imports
from openpyxl import Workbook, load_workbook


class ExcelPipeline:
    """Creates/updates spider-specific Excel file and prints final summary."""

    def open_spider(self, spider):
        self.spider_root = Path.home() / "Documents" / spider.podcast_brand / spider.name.capitalize()
        self.spider_root.mkdir(parents=True, exist_ok=True)

        self.excel_path = self.spider_root / f"{spider.name}.xlsx"
        if self.excel_path.exists():
            self.wb = load_workbook(self.excel_path)
            self.sheet = self.wb.active
        else:
            self.wb = Workbook()
            self.sheet = self.wb.active
            self.sheet.append([
                "Title", "PDF URL", "PDF Path", "MP3 URL", "MP3 Path",
                "Page URL", "Release Date", "Release Year", "Status"
            ])

            self.wb.save(self.excel_path)

        self.total_items = 0

    def process_item(self, item, spider):
        self.sheet.append([
            item.get("title"),
            item.get("pdf_url"),
            item.get("pdf_path"),
            item.get("mp3_url"),
            item.get("mp3_path"),
            item.get("url"),
            item.get("release_date"),
            item.get("release_year"),
            "Downloaded"
        ])
        self.total_items += 1
        
        return item

    def close_spider(self, spider):
        # Save Excel
        self.wb.save(self.excel_path)
        spider.six_minutes_logger.info(f"\nExcel file saved at {self.excel_path}")
        spider.six_minutes_logger.info(f"Total podcasts processed: {self.total_items}")

        # === Scrapy stats ===
        stats = spider.crawler.stats.get_stats()
        total_items = stats.get("item_scraped_count", 0)  # Excel rows
        total_requests = stats.get("downloader/request_count", 0)
        pdf_downloaded = stats.get("files/pdf_downloaded", 0)
        mp3_downloaded = stats.get("files/mp3_downloaded", 0)

        # === User-friendly summary ===
        spider.six_minutes_logger.info(f"\nExcel file saved at {self.excel_path}")
        spider.six_minutes_logger.info("==== Crawl Summary ====")
        spider.six_minutes_logger.info(f"Total requests sent: {total_requests}")
        spider.six_minutes_logger.info(f"Total items scraped (Excel rows): {total_items}")
        spider.six_minutes_logger.info(f"Total PDFs downloaded: {pdf_downloaded}")
        spider.six_minutes_logger.info(f"Total MP3s downloaded: {mp3_downloaded}")
        spider.six_minutes_logger.info("========================\n")
        
