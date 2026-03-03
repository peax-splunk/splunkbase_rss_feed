# Splunkbase RSS Feed

Generate an RSS 2.0 feed from the Splunkbase API. One Python script. No HTTP server—output is a static XML file you can host anywhere (e.g. GitHub Pages).

## Features

- **Latest apps** – Sorted by most recently updated (`order=latest`)
- **Per-item title** – `App Name - v1.2.3` with ` (Archived)` when applicable
- **Author** – Display name from API (`display_author`)
- **Icon** – App icon URL in each item description
- **Full description** – No truncation; empty descriptions show "No description"

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python splunkbase_rss.py
```

Generates the RSS XML file only. Host the file yourself (e.g. static site, GitHub Pages, CDN).

## Configuration

Edit the globals at the top of `splunkbase_rss.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PAGES_TO_FETCH` | `1` | Pages to fetch (100 apps per page). `0` = all pages. |
| `REQUEST_TIMEOUT` | `10` | API request timeout (seconds). |
| `RSS_MAX_ITEMS` | `100` | Max items in the feed. |
| `OUTPUT_FILE` | `splunkbase_feed.xml` | Output file path. |
| `RSS_FEED_URL` | `https://splunkbase.splunk.com/apps/rss/` | URL used in the feed’s `<atom:link rel="self">`. Set to your public feed URL when hosting. |

## Output

- **File**: `splunkbase_feed.xml` (or path set by `OUTPUT_FILE`)
- **Feed URL**: Whatever you set in `RSS_FEED_URL` once the file is hosted (e.g. GitHub Pages, Vercel, S3).

## Subscribe

Point your RSS reader at the URL where you host the XML (e.g. `https://your-username.github.io/your-repo/apps/rss/`).

Examples: Feedly, Inoreader, RSS Guard, NetNewsWire.

## Official Splunkbase RSS

https://splunkbase.splunk.com/apps/rss/ — official feed is **new apps only**. This project’s feed includes **new and updated** apps (sorted by latest), plus version in the title, archived flag, author name, and full descriptions.

---

One script. Pure RSS.
