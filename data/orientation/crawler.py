#!/usr/bin/env python3
"""
Yhteiskuntaorientaatio Web Crawler

Downloads content from yhteiskuntaorientaatio.fi and saves it
in an organized directory structure. Defaults to English.
"""

import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import logging

import requests
from bs4 import BeautifulSoup

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_CYAN = "\033[36m"

logger = logging.getLogger(__name__)


def supports_color(stream):
    """Return True if the stream supports ANSI colors."""
    if os.getenv("NO_COLOR") is not None:
        return False
    if os.getenv("TERM") == "dumb":
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def colorize(text, color, enabled):
    """Apply ANSI color to text if enabled."""
    if not enabled or not color:
        return text
    return f"{color}{text}{ANSI_RESET}"


class ColorFormatter(logging.Formatter):
    """Logging formatter with ANSI colors."""

    LEVEL_COLORS = {
        logging.DEBUG: ANSI_CYAN,
        logging.INFO: ANSI_GREEN,
        logging.WARNING: ANSI_YELLOW,
        logging.ERROR: ANSI_RED,
        logging.CRITICAL: ANSI_RED + ANSI_BOLD,
    }

    def __init__(self, color_enabled):
        super().__init__(fmt='%(asctime)s - %(levelname)s - %(message)s')
        self.color_enabled = color_enabled

    def format(self, record):
        original_levelname = record.levelname
        if self.color_enabled:
            color = self.LEVEL_COLORS.get(record.levelno)
            if color:
                record.levelname = f"{color}{record.levelname}{ANSI_RESET}"
        result = super().format(record)
        record.levelname = original_levelname
        return result


def configure_logging(color_enabled):
    """Configure logging with optional color output."""
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(ColorFormatter(color_enabled))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


class ProgressBar:
    """Simple ASCII progress bar with optional colors."""

    def __init__(self, enabled, color_enabled, width=32):
        self.enabled = enabled
        self.color_enabled = color_enabled
        self.width = width
        self.last_len = 0

    def update(self, visited, remaining):
        if not self.enabled:
            return

        total = max(visited + remaining, 1)
        ratio = min(visited / total, 1.0)
        filled = int(ratio * self.width)
        bar_plain = "#" * filled + "-" * (self.width - filled)
        line_plain = f"[{bar_plain}] {visited}/{total} visited | {remaining} queued"

        if self.color_enabled:
            filled_bar = colorize("#" * filled, ANSI_GREEN, True)
            empty_bar = colorize("-" * (self.width - filled), ANSI_DIM, True)
            bar = f"{filled_bar}{empty_bar}"
            visited_text = colorize(str(visited), ANSI_GREEN, True)
            total_text = colorize(str(total), ANSI_BLUE, True)
            remaining_text = colorize(str(remaining), ANSI_YELLOW, True)
            line = f"[{bar}] {visited_text}/{total_text} visited | {remaining_text} queued"
        else:
            line = line_plain

        pad = max(0, self.last_len - len(line_plain))
        print(f"\r{line}{' ' * pad}", end='', file=sys.stdout, flush=True)
        self.last_len = len(line_plain)

    def finish(self):
        if not self.enabled:
            return
        print(file=sys.stdout)


class OrientationCrawler:
    """Crawler for yhteiskuntaorientaatio.fi content."""

    def __init__(
        self,
        base_url="https://yhteiskuntaorientaatio.fi",
        language="en",
        output_dir=None,
        progress_enabled=True,
        progress_color_enabled=True,
    ):
        self.base_url = base_url.rstrip('/')
        self.language = language.strip('/').lower()
        if not self.language:
            raise ValueError("language must be a non-empty string")

        default_output = Path(__file__).resolve().parent / self.language
        self.output_dir = Path(output_dir) if output_dir else default_output

        parsed_base = urlparse(self.base_url)
        self.allowed_netlocs = {parsed_base.netloc}
        if parsed_base.netloc and not parsed_base.netloc.startswith('www.'):
            self.allowed_netlocs.add(f"www.{parsed_base.netloc}")

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
        self.progress = ProgressBar(
            enabled=progress_enabled,
            color_enabled=progress_color_enabled,
        )

    def is_valid_url(self, url):
        """Check if URL should be crawled."""
        parsed = urlparse(url)

        # Only crawl same host
        if parsed.netloc and parsed.netloc not in self.allowed_netlocs:
            return False

        # Only content in the selected language
        if not parsed.path.startswith(f"/{self.language}/"):
            return False

        # Skip certain file types
        skip_extensions = (
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
            '.zip', '.rar', '.7z', '.doc', '.docx', '.xls', '.xlsx',
            '.ppt', '.pptx'
        )
        if parsed.path.lower().endswith(skip_extensions):
            return False

        return True

    def normalize_url(self, url):
        """Normalize URL for consistency."""
        # Remove fragments and query parameters
        url = url.split('#')[0].split('?')[0]
        # Remove trailing slash for consistency
        if url.endswith('/') and url != self.base_url + '/':
            url = url.rstrip('/')
        return url

    def get_file_path(self, url):
        """Convert URL to local file path."""
        parsed = urlparse(url)
        path = unquote(parsed.path)

        # Remove language prefix
        prefix = f"/{self.language}"
        if path.startswith(prefix):
            path = path[len(prefix):]

        # Handle root
        if not path or path == '/':
            path = 'index'

        # Remove leading slash
        path = path.lstrip('/')
        if path.endswith('/'):
            path = path[:-1]

        # Add .html extension if needed
        if not path.endswith('.html'):
            path = path + '.html'

        return self.output_dir / path

    def extract_main_content(self, soup):
        """Extract main content from the page."""
        main_content = (
            soup.find('main')
            or soup.find('article')
            or soup.find('div', class_='entry-content')
            or soup.find('div', class_='content')
        )
        if main_content:
            return main_content

        body = soup.find('body')
        if body:
            # Remove navigation and footer elements
            for tag in body.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                tag.decompose()
            return body

        return soup

    def extract_links(self, soup, current_url):
        """Extract all valid links from the page."""
        links = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith(('mailto:', 'tel:')):
                continue
            full_url = urljoin(current_url, href)
            full_url = self.normalize_url(full_url)

            if self.is_valid_url(full_url):
                links.add(full_url)

        return links

    def save_page(self, url, content):
        """Save page content to file."""
        file_path = self.get_file_path(url)
        file_path.parent.mkdir(parents=True, exist_ok=True)

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

        html = self.fetch_page(url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        main_content = self.extract_main_content(soup)

        title = soup.title.string if soup.title and soup.title.string else 'Yhteiskuntaorientaatio'
        clean_html = f"""<!DOCTYPE html>
<html lang="{self.language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="source" content="{url}">
</head>
<body>
{main_content.prettify() if main_content else ''}
</body>
</html>
"""

        self.save_page(url, clean_html)

        new_links = self.extract_links(soup, url)
        for link in new_links:
            if link not in self.visited_urls:
                self.to_visit.add(link)

        time.sleep(self.delay)

    def crawl(self, start_url):
        """Start crawling from the provided URL."""
        self.to_visit.add(self.normalize_url(start_url))

        logger.info(f"Starting crawl from {start_url}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")

        self.progress.update(len(self.visited_urls), len(self.to_visit))

        while self.to_visit:
            url = self.to_visit.pop()
            self.process_page(url)
            self.progress.update(len(self.visited_urls), len(self.to_visit))

        self.progress.finish()
        logger.info(f"Crawl complete! Visited {len(self.visited_urls)} pages")
        self.save_statistics()

    def save_statistics(self):
        """Save crawl statistics."""
        stats_file = self.output_dir / 'crawl_stats.txt'
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                f.write("Yhteiskuntaorientaatio Crawl Statistics\n")
                f.write(f"{'=' * 44}\n")
                f.write(f"Total pages crawled: {len(self.visited_urls)}\n")
                f.write(f"Base URL: {self.base_url}\n")
                f.write(f"Language: {self.language}\n")
                f.write("\nCrawled URLs:\n")
                for url in sorted(self.visited_urls):
                    f.write(f"  - {url}\n")
            logger.info(f"Statistics saved to {stats_file}")
        except Exception as e:
            logger.error(f"Error saving statistics: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Crawl yhteiskuntaorientaatio.fi learning materials'
    )
    parser.add_argument(
        '--language',
        '-l',
        default='en',
        help='Language to crawl (default: en)'
    )
    parser.add_argument(
        '--output',
        '-o',
        default=None,
        help='Output directory for downloaded content'
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--base-url',
        default='https://yhteiskuntaorientaatio.fi',
        help='Base URL for the site (default: https://yhteiskuntaorientaatio.fi)'
    )
    parser.add_argument(
        '--start-url',
        default=None,
        help='Starting URL for crawl (default: base + /<lang>/learning-materials)'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bar'
    )

    args = parser.parse_args()

    start_url = args.start_url or f"{args.base_url.rstrip('/')}/{args.language}/learning-materials"
    output_dir = args.output

    log_color_enabled = supports_color(sys.stderr) and not args.no_color
    progress_color_enabled = supports_color(sys.stdout) and not args.no_color
    progress_enabled = sys.stdout.isatty() and not args.no_progress

    global logger
    logger = configure_logging(log_color_enabled)

    crawler = OrientationCrawler(
        base_url=args.base_url,
        language=args.language,
        output_dir=output_dir,
        progress_enabled=progress_enabled,
        progress_color_enabled=progress_color_enabled,
    )
    crawler.delay = args.delay

    try:
        crawler.crawl(start_url=start_url)
    except KeyboardInterrupt:
        crawler.progress.finish()
        logger.info("Crawl interrupted by user")
        crawler.save_statistics()
    except Exception as e:
        crawler.progress.finish()
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
