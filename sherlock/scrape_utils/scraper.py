"""Scraper class for recursively scraping web data from a given URL.

This class will recursively grab all sub-links from a given URL
and scrape them to individual text files."""

from typing import Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel
from selenium import webdriver

from sherlock.file_utils.writer import write_file


class Scraper(BaseModel):
    """Scraper class for recursively scraping web data from a given URL.

    Attributes:
    base_url (str): The URL to start the scraping process.
    links (dict): A dictionary of links and representative text.
    """

    base_url: Optional[str] = None
    source_url: str
    links: dict[str, Optional[str]] = {}
    max_entries: Optional[int] = None
    ignore_values: list[str] = []

    def __init__(
        self,
        source_url: str,
        base_url: Optional[str] = None,
        ignore_values: list[str] = [],
    ):
        """Initialize the Scraper class."""
        super().__init__(
            source_url=source_url,
            base_url=base_url,
            ignore_values=ignore_values,
        )

        # If no base URL is provided, use the source URL (but only get the domain)
        if not self.base_url:
            self.base_url = f'https://{self.source_url.split("//")[1].split("/")[0]}'

        print(f"Starting scraping process for: {self.base_url}")

        if not self.base_url.startswith("http"):
            raise ValueError("URL must start with http or https.")

    def start(self):
        """Start the scraping process."""
        self.get_page_sublinks(self.source_url)

    def get_page_sublinks(self, url: str):
        """Get all sub-links from a given page."""

        for ignore_value in self.ignore_values:
            if ignore_value in url:
                return

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

        if len(page_text) == 0:
            return

        print(f"Scraped: {url} ({len(page_text)} characters)")

        write_file(base_url=self.base_url, sub_url=url, content=page_text)

        if self.max_entries and len(self.links) >= self.max_entries:
            print(f"Reached maximum entries: {self.max_entries}")
            return

        for link in page.find_all("a"):
            link_href = link.get("href")

            if link_href is None:
                continue

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
        # Instantiate ChromeOptions
        chrome_options = webdriver.ChromeOptions()

        # Activate headless mode
        chrome_options.add_argument("--headless=new")

        # Instantiate a webdriver instance
        driver = webdriver.Chrome(options=chrome_options)

        # Visit the target website with Chrome web driver
        driver.get(url)

        # Wait for elements to load
        driver.implicitly_wait(10)

        # Parse page source to BeautifulSoup for Javascript support
        return BeautifulSoup(driver.page_source, "html.parser")


if __name__ == "__main__":
    import os
    import shutil
    from pprint import pprint

    URL = "https://www.cde.state.co.us/postsecondary/icap"

    IGNORE_SUBVALUES = [
        "cde_calendar/",
        "accountability/",
        "schoolview/",
        "mailto:",
        "/cdeawards",
    ]

    if os.path.exists("data"):
        shutil.rmtree("data")
    scraper = Scraper(source_url=URL, ignore_values=IGNORE_SUBVALUES)

    scraper.start()

    pprint(scraper.links)
