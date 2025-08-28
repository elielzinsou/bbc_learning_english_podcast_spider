# Standard library imports
import re

# Third-party imports
from scrapy import signals
import scrapy
import logging

# Local application imports
from bbc_learning_english_podcast_spider.items import SixMinuteEnglishPodcastSpiderItem


class SixMinuteEnglishSpider(scrapy.Spider):
    name = "six_minutes_english"
    allowed_domains = ["bbc.co.uk"]
    start_urls = [
        "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
    ]

    # Keep console quieter by default (you can also put this in settings.py)
    custom_settings = {
        "LOG_LEVEL": "ERROR",
        # Optional niceties:
        # "AUTOTHROTTLE_ENABLED": True,
        # "DOWNLOAD_DELAY": 0.25,
    }

    def __init__(self, years=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Track successful fetch count
        self.success_count = 0
        
        # years: comma-separated list like "2021,2023"
        if years:
            # Normalize and keep as strings
            self.target_years = [y.strip() for y in years.split(",") if y.strip()]
        else:
            self.target_years = None  # scrape all if not provided

        # Use your own logger
        self.six_minutes_logger = logging.getLogger("six_minutes_english_logger")
        self.six_minutes_logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.six_minutes_logger.addHandler(handler)
        
        # Informative startup message
        print("")
        print("=" * 80)
        print("🎧 Welcome to BBC Learning English - 6 Minute English Spider")
        print("This spider extracts podcast metadata (number, title, audio, pdf, date).")
        if self.target_years:
            print(f"📌 Filtering podcasts for years: {', '.join(self.target_years)}")
        else:
            print("⚠ No year filter applied, scraping all available podcasts.")
        print("=" * 80)
        print("")

    # --- Helpers -------------------------------------------------------------

    @staticmethod
    def _extract_date_and_year(raw_text: str):
        """
            raw_text example from listing <h3>:
            'Episode 250828  /  28 Aug 2025'
        """
        raw = " ".join((raw_text or "").split())
        match = re.search(r"(\d{1,2}\s+\w+\s+(\d{4}))", raw)
        if not match:
            return None, None
        release_date = match.group(1).strip()
        release_year = match.group(2)
        return release_date, release_year


    # --- Spiders -------------------------------------------------------------
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        
        return spider
    
    def parse(self, response):
        """
            The page has two main containers:
            1) A featured block with the most recent episode
            2) A wrapper containing all the remaining ones
            Both share a repeated structure under `.widget-bbcle-coursecontentlist .text`.
            We extract date+year from the listing and filter BEFORE requesting details.
        """
        blocks = response.css(".widget-bbcle-coursecontentlist .text")

        seen = set()  # avoid accidental dup requests if any
        for block in blocks:
            link = block.css("h2 a::attr(href)").get()
            if not link:
                continue

            # Get listing info
            title = (block.css("h2 a::text").get() or "").strip()
            number = (block.css(".details h3 b::text").get() or "").strip()

            details_text = " ".join(block.css(".details h3 ::text").getall())
            release_date, release_year = self._extract_date_and_year(details_text)

            # Year filter happens HERE
            if self.target_years and (release_year is None or release_year not in self.target_years):
                continue

            full_url = response.urljoin(link)
            if full_url in seen:
                continue
            seen.add(full_url)

            # Pass what we already know via meta to avoid re-parsing in detail page
            meta = {
                "title": title,
                "number": number,
                "release_date": release_date,
                "release_year": release_year,
            }
            yield response.follow(full_url, callback=self.parse_podcast, meta=meta)

    def parse_podcast(self, response):
        # Minimal console noise: just show the fetched URL and HTTP status
        self.six_minutes_logger.info(f"Fetched {response.url} [{response.status}]")
        
        if response.status == 200:
            self.success_count += 1
        
        # Take what we can from meta (already parsed on listing)
        item = SixMinuteEnglishPodcastSpiderItem()
        item["number"] = response.meta.get("number")
        item["title"] = response.meta.get("title")
        item["url"] = response.url
        item["release_date"] = response.meta.get("release_date")
        item["release_year"] = response.meta.get("release_year")

        # only extract the heavy stuff we can’t get from listing
        item["pdf_url"] = response.css(".download.bbcle-download-extension-pdf::attr(href)").get()
        item["audio_url"] = response.css(".download.bbcle-download-extension-mp3::attr(href)").get()

        # (Optional) if title/number missing from listing, try a generic fallback:
        if not item["title"]:
            item["title"] = (response.css("h1::text").get() or "").strip()
        if not item["number"]:
            item["number"] = (response.css(".text .details h3 > b::text").get() or "").strip()

        yield item

    
    def spider_closed(self, spider):
        print("")
        print("=" * 80)
        print(f"✅ Total successful fetches: {self.success_count}")
        print("⬇️  Downloading process will start soon...")
        print("=" * 80)
        print("")
