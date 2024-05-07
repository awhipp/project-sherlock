"""Scraper class for recursively scraping web data from a given URL.

This class will recursively grab all sub-links from a given URL
and scrape them to individual text files."""

from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from sherlock.file_utils.writer import write_file


class Scraper(BaseModel):
    """Scraper class for recursively scraping web data from a given URL.

    Attributes:
    base_url (str): The URL to start the scraping process.
    links (dict): A dictionary of links and representative text.
    """

    base_url: str
    links: dict[str, Optional[str]] = {}

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)
        if not self.base_url.startswith("http"):
            raise ValueError("URL must start with http or https.")

    def start(self):
        """Start the scraping process."""
        self.get_page_sublinks(self.base_url)

    def get_page_sublinks(self, url: str):
        """Get all sub-links from a given page."""

        # Remove all window.hash
        if "#" in url:
            url = url.split("#")[0]

        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]

        if url in self.links:
            return

        page: BeautifulSoup = Scraper.scrape(url=url)

        page_text: str = page.get_text()

        self.links[url] = len(page_text)

        write_file(base_url=self.base_url, sub_url=url, content=page_text)

        for link in page.find_all("a"):
            link_href = link.get("href")

            if not link_href.startswith("http"):
                if link_href.startswith("/"):
                    link_href = f"{self.base_url}{link_href}"
                else:
                    link_href = f"{self.base_url}/{link_href}"

            if (
                link_href is not None
                and link_href not in self.links
                and f"{link_href}/" not in self.links
                and self.base_url in link_href
            ):
                self.get_page_sublinks(link_href)

    @staticmethod
    def scrape(url: str) -> BeautifulSoup:
        """Scrape the HTML content of a given URL."""
        response = requests.get(url=url, timeout=10)
        return BeautifulSoup(response.content, "html.parser")


if __name__ == "__main__":
    import os
    import shutil
    from pprint import pprint

    if os.path.exists("data"):
        shutil.rmtree("data")
    scraper = Scraper(base_url="https://evetrade.space")

    scraper.start()

    pprint(scraper.links)
