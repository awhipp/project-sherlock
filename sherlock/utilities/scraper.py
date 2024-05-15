"""Scraper class for recursively scraping web data from a given URL.

This class will recursively grab all sub-links from a given URL
and scrape them to individual text files."""

import datetime
import os
import shutil
from typing import Optional
from typing import Union

import html2text
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sherlock.utilities.file_type import FileType
from sherlock.utilities.metadata import Metadata
from sherlock.utilities.writer import write_file


html2text = html2text.HTML2Text()
html2text.ignore_links = True

chrome_options = webdriver.ChromeOptions()
ua = UserAgent()
userAgent = ua.chrome
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--headless=old")
chrome_options.add_argument(f"user-agent={userAgent}")
chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

# Add headers to mimic a browser visit

driver = webdriver.Chrome(options=chrome_options)


class Scraper(BaseModel):
    """Scraper class for recursively scraping web data from a given URL.

    Attributes:
    base_url (str): The URL to start the scraping process.
    links (dict): A dictionary of links and representative text.
    ignore_values (list): A list of values to ignore when scraping.
    max_depth (int): The maximum depth to scrape.
    source_url (str): The URL to start the scraping process.
    """

    source_url: str
    collection_name: str
    base_url: Optional[str]
    links: dict[str, Optional[str]]
    ignore_values: list[str]
    max_depth: int

    def __init__(
        self,
        source_url: str,
        collection_name: str,
        base_url: Optional[str] = None,
        ignore_values: list[str] = [],
        max_depth: int = 1,
    ):
        """Initialize the Scraper class."""
        super().__init__(
            collection_name=collection_name,
            source_url=source_url,
            base_url=base_url,
            links={},
            ignore_values=ignore_values,
            max_depth=max_depth,
        )
        # Clear the output directory
        output_dir = f"./web_docs/{self.collection_name}"
        print(f"Clearing output directory: {output_dir}")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        # If no base URL is provided, use the source URL (but only get the domain)
        if not self.base_url:
            self.base_url = f'https://{self.source_url.split("//")[1].split("/")[0]}'

        print(f"Starting scraping process for: {self.source_url}")

        if not self.source_url.startswith("http"):
            raise ValueError("URL must start with http or https.")

    def start(self):
        """Start the scraping process."""
        import time

        start_time = time.time()
        self.get_page_sublinks(url=self.source_url, depth=0)
        print(f"Scraped {len(self.links)} pages.")
        print(f"Elapsed time: {time.time() - start_time:.2f} seconds.")

    def get_page_sublinks(self, url: str, depth: int = 0):
        """Get all sub-links from a given page.

        Args:
        url (str): The URL to scrape.
        depth (int): The depth of the URL.
        """

        if depth > self.max_depth:
            return

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

        page, file_type = Scraper.scrape(url=url)

        if page is None:
            self.links[url] = 0
            return

        if isinstance(page, BeautifulSoup):
            page_text: str = html2text.handle(str(page))
        elif isinstance(page, bytes):
            if file_type == FileType.PDF:
                # Write to PDF file
                self.links[url] = write_file(
                    collection_name=self.collection_name,
                    url=url,
                    content=page,
                    file_type=FileType.PDF,
                    depth=depth,
                )
                return
            elif file_type == FileType.DOCX:
                # Write to DOCX file
                self.links[url] = write_file(
                    collection_name=self.collection_name,
                    url=url,
                    content=page,
                    file_type=FileType.DOCX,
                    depth=depth,
                )
                return
        else:
            raise ValueError(
                f"Scrape result must be BeautifulSoup or bytes object (received: {type(page)}).",
            )

        # Trim blank lines
        page_text = "\n".join([line for line in page_text.split("\n") if line.strip()])

        if len(page_text) == 0:
            self.links[url] = 0
            return

        page_text = (
            Metadata(
                title=url.split("/")[-1],
                source=url,
                file_type=file_type,
                retrieved_date=datetime.datetime.now().strftime("%Y-%m-%d"),
            ).to_markdown()
            + page_text
        )

        self.links[url] = write_file(
            collection_name=self.collection_name,
            url=url,
            content=page_text,
            file_type=FileType.HTML,
            depth=depth,
        )

        if isinstance(page, BeautifulSoup):
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
                    self.get_page_sublinks(url=link_href, depth=depth + 1)

    @staticmethod
    def scrape(url: str) -> tuple[Union[bytes, BeautifulSoup], FileType]:
        """Scrape the content of a given URL.

        Args:
        url (str): The URL to scrape.

        Returns:
        tuple: The scraped content and file type."""

        r = requests.get(url, timeout=10)

        # if r.status_code != 200:
        #     print(f"Failed to scrape {url} with status code {r.status_code}")
        #     return None, FileType.Unsupported

        content_type = r.headers.get("content-type")

        # HTML parsing
        if "text/html" in content_type:
            # Visit the target website with Chrome web driver
            driver.get(url)
            # Wait for elements to load
            driver.implicitly_wait(10)

            # Parse page source to BeautifulSoup for Javascript support
            return BeautifulSoup(driver.page_source, "html.parser"), FileType.HTML

        # PDF parsing
        elif "application/pdf" in content_type:
            return r.content, FileType.PDF

        # Word Document parsing
        elif (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            in content_type
        ):
            return r.content, FileType.DOCX

        # Excel Document parsing
        elif (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in content_type
            or "application/vnd.ms-excel" in content_type
        ):
            print(f"Unsupported content type: {content_type}")
            return None, FileType.Unsupported

        # CSV Document parsing
        elif "text/csv" in content_type:
            print(f"Unsupported content type: {content_type}")
            return None, FileType.Unsupported

        elif (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            in content_type
        ):
            print(f"Unsupported content type: {content_type}")
            return None, FileType.Unsupported

        # Unsupported
        else:
            print(f"Unsupported content type: {content_type}")
            return None, FileType.Unsupported


if __name__ == "__main__":

    scraper = Scraper(
        collection_name="Colorado ICAP",
        source_url="https://www.cde.state.co.us/postsecondary/icap",
    )

    scraper.start()

    # Print number of links and total characters scraped
    print(f"Total links scraped: {len(scraper.links)}")
    print(f"Total characters scraped: {sum(scraper.links.values())}")
