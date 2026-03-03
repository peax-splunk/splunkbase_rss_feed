# Splunkbase RSS Feed

Generate an RSS 2.0 feed from the [Splunkbase](https://splunkbase.splunk.com/) API for new and updated Splunk apps. One Python script—no HTTP server. Output is a static XML file you can host anywhere (e.g. GitHub Pages, Vercel, S3).

**Repository:** [github.com/peax-splunk/splunkbase_rss_feed](https://github.com/peax-splunk/splunkbase_rss_feed)

## Features

- **Latest apps** – Sorted by most recently updated (`order=latest`)
- **Per-item title** – `App Name - v1.2.3` with `(Archived)` when applicable
- **Author** – Display name from API (`display_author`)
- **Icon** – App icon URL in each item description
- **Full description** – No truncation; empty descriptions show "No description"
- **Unique GUID per version** – Each app version is a distinct feed item so RSS readers can notify on updates

## Install

```bash
git clone https://github.com/peax-splunk/splunkbase_rss_feed.git
cd splunkbase_rss_feed
pip install -r requirements.txt
```

## Usage

```bash
python splunkbase_rss.py
```

Generates the RSS XML file. Host the file yourself (e.g. static site, GitHub Pages, CDN).

## Configuration

Edit the globals at the top of `splunkbase_rss.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PAGES_TO_FETCH` | `1` | Pages to fetch (100 apps per page). `0` = all pages. |
| `REQUEST_TIMEOUT` | `10` | API request timeout (seconds). |
| `RSS_MAX_ITEMS` | `100` | Max items in the feed. |
| `OUTPUT_FILE` | `splunkbase_rss_feed.xml` | Output file path. |
| `RSS_FEED_URL` | `https://splunkbase.splunk.com/apps/rss/` | URL used in the feed’s `<atom:link rel="self">`. Set to your public feed URL when hosting. |

## Output

- **File**: `splunkbase_rss_feed.xml` (or path set by `OUTPUT_FILE`)
- **Feed URL**: Whatever you set in `RSS_FEED_URL` once the file is hosted.

## Subscribe

Point your RSS reader at the URL where you host the XML (e.g. `https://peax-splunk.github.io/splunkbase_rss_feed/splunkbase_rss_feed.xml` or your own deployment).

Examples: Feedly, Inoreader, RSS Guard, NetNewsWire.

## Official Splunkbase RSS

[Splunkbase RSS](https://splunkbase.splunk.com/apps/rss/) — the official feed is **new apps only**. This project’s feed includes **new and updated** apps (sorted by latest), plus version in the title, archived flag, author name, and full descriptions.

---

One script. Pure RSS.
