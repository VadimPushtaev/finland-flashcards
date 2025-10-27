# InfoFinland Directory

This directory is intended to store documents and content downloaded from [InfoFinland.fi](https://www.infofinland.fi/sv).

## Purpose

InfoFinland is a multilingual website providing reliable information for people planning to move to Finland or already living there. The content covers topics such as:

- Moving to Finland
- Settling in Finland
- Work and entrepreneurship
- Finnish and Swedish language
- Housing
- Education
- Health
- Family
- Leisure
- Information about Finland

## Setup

Use Poetry for dependency management:

```bash
# First-time setup
poetry install
```

## Usage

Run the crawler to download all Swedish content from InfoFinland:

```bash
poetry run python data/infofinland/crawler.py -o data/infofinland/content
```

### Options

- `--output DIR` or `-o DIR`: Specify output directory (default: `content`)
- `--delay SECONDS` or `-d SECONDS`: Delay between requests in seconds (default: 1.0)
- `--start-url URL` or `-s URL`: Starting URL for crawl

### Examples

```bash
# Download to a custom directory
poetry run python data/infofinland/crawler.py --output my_content

# Increase delay to 2 seconds between requests
poetry run python data/infofinland/crawler.py --delay 2.0

# Start from a specific page
poetry run python data/infofinland/crawler.py --start-url https://www.infofinland.fi/sv/arbete-och-entreprenorskap
```

## Output

The crawler will:
- Download all pages from the Swedish version of InfoFinland
- Save them as clean HTML files in the output directory
- Maintain the URL structure in the local file system
- Generate a `crawl_stats.txt` file with crawl statistics
- Respect rate limiting (1 second delay between requests by default)

## Source

- Website: https://www.infofinland.fi/sv
- Language: Swedish (Svenska)
- Publisher: City of Helsinki
- Funders: The Finnish state and the cities of Helsinki, Espoo, Vantaa, and Kauniainen

