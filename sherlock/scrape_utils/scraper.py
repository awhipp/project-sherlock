"""Scraper class for recursively scraping web data from a given URL.

This class will recursively grab all sub-links from a given URL
and scrape them to individual text files."""

import requests
import html2text
import datetime
from typing import Optional, Union, Tuple

from bs4 import BeautifulSoup
from pydantic import BaseModel
from selenium import webdriver

from io import BytesIO
import docx2txt
import requests, io
import pandas as pd
from pypdf import PdfReader  # you can also use pypdf>=3.1.0

from sherlock.scrape_utils.metadata import Metadata
from sherlock.file_utils.writer import write_file
from sherlock.file_utils.file_type import FileType

html2text = html2text.HTML2Text()
html2text.ignore_links = True

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)


class Scraper(BaseModel):
    """Scraper class for recursively scraping web data from a given URL.

    Attributes:
    base_url (str): The URL to start the scraping process.
    links (dict): A dictionary of links and representative text.
    """

    source_url: str
    base_url: Optional[str]
    links: dict[str, Optional[str]]
    max_entries: Optional[int]
    max_size: Optional[int]
    ignore_values: list[str]

    def __init__(
        self,
        source_url: str,
        base_url: Optional[str] = None,
        links: dict[str, Optional[str]] = {},
        max_entries: Optional[int] = None,
        max_size: Optional[int] = None,
        ignore_values: list[str] = [],
    ):
        """Initialize the Scraper class."""
        super().__init__(
            source_url=source_url,
            base_url=base_url,
            links={},
            max_entries=None,
            max_size=None,
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

        page, file_type = Scraper.scrape(url=url)

        if isinstance(page, BeautifulSoup):
            page_text: str = html2text.handle(str(page))
        elif isinstance(page, str):
            page_text: str = page
        else:
            raise ValueError("Scrape result must be BeautifulSoup or str object.")
        
        # Trim blank lines
        page_text = "\n".join([line for line in page_text.split("\n") if line.strip()])

        # Check if its a PDF page

        self.links[url] = len(page_text)

        if len(page_text) == 0:
            return
        
        page_text = Metadata(
            title=url.split("/")[-1],
            source=url,
            file_type=file_type,
            retrieved_date=datetime.datetime.now().strftime("%Y-%m-%d"),
        ).to_markdown() + page_text

        print(f"Scraped: {url} ({len(page_text)} characters)")

        total_size = write_file(base_url=self.base_url, sub_url=url, content=page_text)

        # Check if we have reached the maximum entries
        if self.max_entries and len(self.links) >= self.max_entries:
            print(f"Reached maximum entries: {self.max_entries}")
            return
        
        # Check if we have reached the maximum size
        if self.max_size and total_size >= self.max_size:
            print(f"Reached maximum size: {self.max_size}")
            return
        

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
                    self.get_page_sublinks(link_href)

    @staticmethod
    def scrape(url: str) -> Tuple[Union[str, BeautifulSoup], FileType]:
        """Scrape the content of a given URL.
        
        Args:
        url (str): The URL to scrape.
        
        Returns:
        Tuple[Union[str, BeautifulSoup], str]: The scraped content and file type."""

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print(f"Failed to scrape {url} with status code {r.status_code}")
            return "", FileType.HTML
        
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
            page_text: str = ""
            with io.BytesIO(r.content) as open_pdf_file:
                reader = PdfReader(open_pdf_file)

                for _, page in enumerate(reader.pages):
                    page_text += page.extract_text()
            
            return page_text, FileType.PDF
        
        # Word Document parsing
        elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type: 
            return docx2txt.process(BytesIO(r.content)), FileType.DOCX
        

        # Excel Document parsing
        elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type or "application/vnd.ms-excel" in content_type:
            return pd.read_excel(BytesIO(r.content)).to_markdown(), FileType.XLSX
        
        # CSV Document parsing
        elif "text/csv" in content_type:
            return pd.read_csv(BytesIO(r.content)).to_markdown(), FileType.CSV

        # Unsupported
        else:
            raise ValueError(f"URL ({url}) has an unsupported content type: {content_type}.")


if __name__ == "__main__":
    import os
    import shutil
    from pprint import pprint

    URL = "https://www.cde.state.co.us/postsecondary/icap"
    # URL = "https://www.cde.state.co.us/cdereval/2021-2022chronicabsenteeismbydistrict"

    IGNORE_SUBVALUES = [
        "cde_calendar/",
        "accountability/",
        "schoolview/",
        "mailto:",
        "/cdeawards",
    ]

    if os.path.exists("web_docs"):
        shutil.rmtree("web_docs")

    # file_max = 1024 * 1024 * 25  # 25 MB

    scraper = Scraper(source_url=URL, ignore_values=IGNORE_SUBVALUES)

    scraper.start()

    pprint(scraper.links)
