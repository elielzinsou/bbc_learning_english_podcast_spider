# Standard library imports
from pathlib import Path
import logging
import time
import re

# Third-party imports
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
        "LOG_LEVEL": "WARNING",
        "ITEM_PIPELINES": {
            "bbc_learning_english_podcast_spider.pipelines.CustomFilesPipeline": 100,
            "bbc_learning_english_podcast_spider.pipelines.ExcelPipeline": 200,
        },
        # Root where FilesPipeline will save files
        "FILES_STORE": str(Path.home() / "Documents" / "BBC_English_Podcast"),
    }

    def __init__(self, years=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # years: comma-separated list like "2021,2023"
        # Normalize and keep as strings
        self.target_years = (
            [y.strip() for y in years.split(",") if y.strip()] if years else None
        )

        # Custom logger
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
        print(
            "This spider extracts podcast metadata (number, title, audio, pdf, date)."
        )
        if self.target_years:
            print(f"📌 Filtering podcasts for years: {', '.join(self.target_years)}")
        else:
            print("⚠ No year filter applied, scraping all available podcasts.")
        print("=" * 80)
        print("")
        time.sleep(2)

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
        return match.group(1).strip(), match.group(2)

    # --- Spiders -------------------------------------------------------------
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

            # Listing info
            title = (block.css("h2 a::text").get() or "").strip()
            number = (block.css(".details h3 b::text").get() or "").strip()
            details_text = " ".join(block.css(".details h3 ::text").getall())
            release_date, release_year = self._extract_date_and_year(details_text)

            # Year filter
            if self.target_years and (
                release_year is None or release_year not in self.target_years
            ):
                continue

            full_url = response.urljoin(link)
            if full_url in seen:
                continue
            seen.add(full_url)

            # For stats: how many episode pages we schedule
            self.crawler.stats.inc_value("episodes/scheduled")

            # Pass pre-extracted metadata via meta
            meta = {
                "title": title,
                "number": number,
                "release_date": release_date,
                "release_year": release_year,
            }
            yield response.follow(full_url, callback=self.parse_podcast, meta=meta)

    def parse_podcast(self, response):
        # Minimal console noise: just show fetched URL and HTTP status
        if response.status == 200:
            self.crawler.stats.inc_value("episodes/fetched")
        self.six_minutes_logger.info(f"Fetched {response.url} [{response.status}]")

        # Populate item with metadata from meta
        item = SixMinuteEnglishPodcastSpiderItem()
        item["number"] = response.meta.get("number")
        item["title"] = response.meta.get("title")
        item["url"] = response.url
        item["release_date"] = response.meta.get("release_date")
        item["release_year"] = response.meta.get("release_year")

        # Extract heavy stuff only: PDF & MP3 URLs for FilesPipeline
        item["pdf_url"] = response.css(
            ".download.bbcle-download-extension-pdf::attr(href)"
        ).get()
        item["mp3_url"] = response.css(
            ".download.bbcle-download-extension-mp3::attr(href)"
        ).get()

        # Fallback if metadata missing
        if not item["title"]:
            item["title"] = (response.css("h1::text").get() or "").strip()
        if not item["number"]:
            item["number"] = (
                response.css(".text .details h3 > b::text").get() or ""
            ).strip()

        yield item
