#!/usr/bin/env python3
"""
InfoFinland Web Crawler

Downloads content from the Swedish version of InfoFinland.fi
and saves it in an organized directory structure.
"""

import os
import time
import re
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
import logging

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfoFinlandCrawler:
    """Crawler for InfoFinland.fi Swedish content."""

    def __init__(self, base_url="https://www.infofinland.fi/sv", output_dir="content"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.visited_urls = set()
        self.to_visit = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting: seconds between requests
        self.delay = 1.0

    def is_valid_url(self, url):
        """Check if URL should be crawled."""
        parsed = urlparse(url)

        # Only crawl InfoFinland.fi URLs
        if parsed.netloc and parsed.netloc != 'www.infofinland.fi':
            return False

        # Only Swedish content
        if not parsed.path.startswith('/sv'):
            return False

        # Skip certain file types
        skip_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.doc', '.docx')
        if parsed.path.lower().endswith(skip_extensions):
            return False

        return True

    def normalize_url(self, url):
        """Normalize URL for consistency."""
        # Remove fragments
        url = url.split('#')[0]
        # Remove trailing slash for consistency
        if url.endswith('/') and url != self.base_url + '/':
            url = url.rstrip('/')
        return url

    def get_file_path(self, url):
        """Convert URL to local file path."""
        parsed = urlparse(url)
        path = unquote(parsed.path)

        # Remove /sv prefix
        if path.startswith('/sv'):
            path = path[3:]

        # Handle root
        if not path or path == '/':
            path = 'index'

        # Remove leading slash
        path = path.lstrip('/')

        # Add .html extension if needed
        if not path.endswith('.html'):
            path = path + '.html'

        return self.output_dir / path

    def extract_main_content(self, soup):
        """Extract main content from the page."""
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

        if main_content:
            return main_content

        # Fallback: return body without nav/footer
        body = soup.find('body')
        if body:
            # Remove navigation and footer elements
            for tag in body.find_all(['nav', 'header', 'footer']):
                tag.decompose()
            return body

        return soup

    def extract_links(self, soup, current_url):
        """Extract all valid links from the page."""
        links = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            full_url = self.normalize_url(full_url)

            if self.is_valid_url(full_url):
                links.add(full_url)

        return links

    def save_page(self, url, content):
        """Save page content to file."""
        file_path = self.get_file_path(url)

        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False

    def fetch_page(self, url):
        """Fetch a single page."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def process_page(self, url):
        """Process a single page: fetch, parse, save, extract links."""
        if url in self.visited_urls:
            return

        self.visited_urls.add(url)

        # Fetch page
        html = self.fetch_page(url)
        if not html:
            return

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Extract and save main content
        main_content = self.extract_main_content(soup)

        # Create a clean HTML document
        clean_html = f"""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{soup.title.string if soup.title else 'InfoFinland'}</title>
    <meta name="source" content="{url}">
</head>
<body>
{main_content.prettify() if main_content else ''}
</body>
</html>
"""

        # Save the page
        self.save_page(url, clean_html)

        # Extract links for further crawling
        new_links = self.extract_links(soup, url)

        # Add new links to queue
        for link in new_links:
            if link not in self.visited_urls:
                self.to_visit.add(link)

        # Rate limiting
        time.sleep(self.delay)

    def crawl(self, start_url=None):
        """Start crawling from the base URL."""
        if start_url is None:
            start_url = self.base_url

        self.to_visit.add(start_url)

        logger.info(f"Starting crawl from {start_url}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")

        while self.to_visit:
            url = self.to_visit.pop()
            self.process_page(url)

            # Log progress
            logger.info(f"Progress: {len(self.visited_urls)} visited, {len(self.to_visit)} remaining")

        logger.info(f"Crawl complete! Visited {len(self.visited_urls)} pages")

        # Save crawl statistics
        self.save_statistics()

    def save_statistics(self):
        """Save crawl statistics."""
        stats_file = self.output_dir / 'crawl_stats.txt'
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                f.write(f"InfoFinland Crawl Statistics\n")
                f.write(f"{'=' * 40}\n")
                f.write(f"Total pages crawled: {len(self.visited_urls)}\n")
                f.write(f"Base URL: {self.base_url}\n")
                f.write(f"\nCrawled URLs:\n")
                for url in sorted(self.visited_urls):
                    f.write(f"  - {url}\n")
            logger.info(f"Statistics saved to {stats_file}")
        except Exception as e:
            logger.error(f"Error saving statistics: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Crawl InfoFinland.fi Swedish content')
    parser.add_argument(
        '--output',
        '-o',
        default='content',
        help='Output directory for downloaded content (default: content)'
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--start-url',
        '-s',
        default='https://www.infofinland.fi/sv',
        help='Starting URL for crawl (default: https://www.infofinland.fi/sv)'
    )

    args = parser.parse_args()

    # Create crawler
    crawler = InfoFinlandCrawler(
        base_url='https://www.infofinland.fi/sv',
        output_dir=args.output
    )
    crawler.delay = args.delay

    # Start crawling
    try:
        crawler.crawl(start_url=args.start_url)
    except KeyboardInterrupt:
        logger.info("\nCrawl interrupted by user")
        crawler.save_statistics()
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == '__main__':
    main()

