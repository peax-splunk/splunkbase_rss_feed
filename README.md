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

## Official Splunkbase RSS

[Splunkbase RSS](https://splunkbase.splunk.com/apps/rss/) — the official feed is **new apps only**. This project’s feed includes **new and updated** apps (sorted by latest), plus version in the title, archived flag, author name, and full descriptions.

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

## GitHub Actions & GitHub Pages

The repo includes a workflow that **builds the feed every hour** and publishes it to GitHub Pages so the feed is always up to date without running the script yourself.

### How it works

1. **Schedule:** The workflow runs on a [cron schedule](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule) every hour (`0 * * * *`).
2. **Build:** It installs dependencies, runs `python splunkbase_rss.py`, and produces `rss.xml` (correct Content-Type when served).
3. **Deploy:** It pushes the feed to the `gh-pages` branch, which GitHub Pages serves.

### Enable the public feed

1. In the repo, go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Choose branch **`gh-pages`** and folder **`/ (root)`**. Save.
4. The workflow will run on the next hour (or run it manually: **Actions → Build and publish RSS feed → Run workflow**).

After the first successful run, the feed is available at:

**https://peax-splunk.github.io/splunkbase_rss_feed/rss.xml**

The `.xml` extension ensures the correct Content-Type so browsers and RSS readers open the feed instead of downloading it.

## Configuration

Edit the globals at the top of `splunkbase_rss.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `PAGES_TO_FETCH` | `1` | Pages to fetch (100 apps per page). `0` = all pages. |
| `REQUEST_TIMEOUT` | `10` | API request timeout (seconds). |
| `RSS_MAX_ITEMS` | `100` | Max items in the feed. |
| `OUTPUT_FILE` | `rss.xml` | Output file path. |
| `RSS_FEED_URL` | `https://peax-splunk.github.io/splunkbase_rss_feed/rss.xml` | URL used in the feed’s `<atom:link rel="self">`. Must match where you host the file. |

## Output

- **File**: `rss.xml` (or path set by `OUTPUT_FILE`)
- **Feed URL**: [https://peax-splunk.github.io/splunkbase_rss_feed/rss.xml](https://peax-splunk.github.io/splunkbase_rss_feed/rss.xml) once GitHub Pages is enabled and the workflow has run.

## Subscribe

Point your RSS reader at:

**https://peax-splunk.github.io/splunkbase_rss_feed/rss.xml**

Examples: Feedly, Inoreader, RSS Guard, NetNewsWire.

---
