# Yhteiskuntaorientaatio Directory

This directory stores documents and content downloaded from
https://yhteiskuntaorientaatio.fi.

## Purpose

Yhteiskuntaorientaatio provides learning materials for Finnish society
orientation. This crawler targets the English learning materials for now,
with language support left open for future Swedish or Finnish crawls.

## Setup

Use Poetry for dependency management:

```bash
# First-time setup
poetry install
```

## Usage

Run the crawler to download English learning materials:

```bash
poetry run python data/orientation/crawler.py -l en -o data/orientation/en
```

### Options

- `--language` or `-l`: Language to crawl (default: `en`)
- `--output` or `-o`: Output directory for downloaded content
- `--delay` or `-d`: Delay between requests in seconds (default: 1.0)
- `--base-url`: Base URL for the site
- `--start-url`: Starting URL for crawl
- `--no-color`: Disable colored log output
- `--no-progress`: Disable the progress bar

### Examples

```bash
# Default English crawl into data/orientation/en
poetry run python data/orientation/crawler.py

# Increase delay to 2 seconds between requests
poetry run python data/orientation/crawler.py --delay 2.0

# Crawl another language path when available
poetry run python data/orientation/crawler.py -l sv -o data/orientation/sv
```

## Output

The crawler will:
- Download pages under the selected language path (e.g., `/en/`)
- Save them as clean HTML files in the output directory
- Maintain the URL structure in the local file system
- Generate a `crawl_stats.txt` file with crawl statistics
- Respect rate limiting (1 second delay between requests by default)
- Show colored logs and a live progress bar in a TTY by default

## Source

- Website: https://yhteiskuntaorientaatio.fi/en/learning-materials
- Language: English (default)
