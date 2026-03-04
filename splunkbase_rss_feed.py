#!/usr/bin/env python3

"""
Splunkbase RSS Feed Generator
Fetches latest apps from Splunkbase API and generates RSS 2.0 feed.
"""

import requests
import math
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring, register_namespace
from xml.dom import minidom
from html import escape

# Register XML namespaces
register_namespace('atom', 'http://www.w3.org/2005/Atom')
register_namespace('dc', 'http://purl.org/dc/elements/1.1/')

# Configuration (edit these to change behavior)
REQUEST_TIMEOUT = 10  # API request timeout (seconds)
PAGES_TO_FETCH = 1    # Pages to fetch (100 apps per page). 0 = all pages.
RSS_MAX_ITEMS = 100
OUTPUT_FILE = Path("rss.xml")  # .xml extension for correct Content-Type when served
RSS_FEED_URL = "https://peax-splunk.github.io/splunkbase_rss_feed/rss.xml"

SPLUNKBASE_API_URL = "https://api.splunkbase.splunk.com/api/v2/apps/"
REQUEST_PARAMS = {
    "order": "latest",  # Sort by most recently updated
    "limit": 100,
    "include": "release,releases,display_author,icon",
    "archive": "all",
    "product": "all"
}


def fetch_latest_apps(max_pages=0):
    """
    Fetch latest apps from Splunkbase API.
    
    Args:
        max_pages: Maximum pages to fetch (0 = all)
    
    Returns:
        List of app dictionaries sorted by updated_time (newest first)
    """
    print("Fetching latest apps from Splunkbase API...")
    
    try:
        response = requests.get(SPLUNKBASE_API_URL, params=REQUEST_PARAMS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    data = response.json()
    total_results = data.get("total", 0)
    total_pages = math.ceil(total_results / 100)
    
    # Limit pages if specified
    if max_pages > 0:
        total_pages = min(total_pages, max_pages)
        print(f"Fetching {total_pages} pages (~{total_pages * 100} apps)")
    else:
        print(f"Fetching all {total_pages} pages (~{total_results} apps)")
    
    apps = []
    for page in range(total_pages):
        print(f"  Page {page + 1}/{total_pages}...", end="\r")
        
        params = REQUEST_PARAMS.copy()
        params["offset"] = page * 100
        
        try:
            response = requests.get(SPLUNKBASE_API_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            page_apps = response.json().get("results", [])
            apps.extend(page_apps)
        except Exception as e:
            print(f"\n  Error fetching page {page + 1}: {e}")
            continue
    
    print(f"\nFetched {len(apps)} apps")
    
    # No need to sort - API already returns apps sorted by "order=latest"
    # Sorting here can change the order within fetched pages
    
    return apps


def format_rfc822_date(iso_timestamp):
    """Convert ISO timestamp to RFC 822 format for RSS."""
    try:
        # Handle both formats: with and without microseconds
        if '.' in iso_timestamp:
            dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
    except:
        return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')


def create_rss_feed(apps, max_items=50):
    """
    Create RSS 2.0 feed from apps list.
    
    Args:
        apps: List of app dictionaries (sorted newest first)
        max_items: Maximum items to include
    """
    # Limit items
    apps = apps[:max_items]
    # Sort by pubDate (updated_time / published_time) latest to oldest
    apps = sorted(apps, key=lambda a: a.get('updated_time', a.get('published_time', '')), reverse=True)
    
    # Create RSS root (namespaces will be auto-declared when elements use them)
    rss = Element('rss')
    rss.set('version', '2.0')
    
    channel = SubElement(rss, 'channel')
    
    # Channel metadata
    SubElement(channel, 'title').text = 'peax - Splunkbase Apps Releases'
    SubElement(channel, 'link').text = 'https://splunkbase.splunk.com/apps/'
    SubElement(channel, 'description').text = 'a list of Newly/updated Splunk apps'
    
    # Self-referencing link (use namespace URI)
    atom_link = SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', RSS_FEED_URL)
    atom_link.set('rel', 'self')
    
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Create items
    for app in apps:
        item = SubElement(channel, 'item')
        
        # Latest version: prefer "release.release_name", then first entry in "releases", else "null"
        if app.get("release"):
            latest_version = app["release"].get("release_name", "null")
        else:
            releases = app.get("releases", [])
            if releases:
                latest_version = releases[0].get("release_name", "null")
            else:
                latest_version = "null"
        
        # Title: "<app name> - v<version>" and append " (Archived)" when is_archived is true
        app_name = app.get('app_name', 'Unknown App')
        title = f"{app_name} - v{latest_version}"
        if app.get('is_archived'):
            title = f"{title} (Archived)"
        SubElement(item, 'title').text = title
        
        # Link (use app_url from API; fallback to built URL if missing)
        app_url = app.get('app_url') or f"https://splunkbase.splunk.com/app/{app.get('id', '')}/"
        SubElement(item, 'link').text = app_url
        
        # Description (HTML formatted and escaped)
        description = app.get('description', '')
        if description:
            # Escape HTML entities in description
            description = escape(description)
            description = f"<p>{description}</p>"
        else:
            description = "<p>No description</p>"
        
        # Add icon if available (icon from include param; fallback to app_icon or default)
        app_icon = app.get('icon') or 'https://cdn.splunkbase.splunk.com/static/image/default_icon.png'
        app_icon = escape(app_icon, quote=True)
        description += f'<img height="36px" width="36px" src="{app_icon}">'
        
        SubElement(item, 'description').text = description
        
        # Creator: display_author.name when include=display_author (escape special characters)
        display_author = app.get('display_author') or {}
        creator = escape(display_author.get('name') or 'Unknown')
        SubElement(item, '{http://purl.org/dc/elements/1.1/}creator').text = creator
        
        # Publication date (use updated_time)
        pub_date = app.get('updated_time', app.get('published_time', ''))
        if pub_date:
            SubElement(item, 'pubDate').text = format_rfc822_date(pub_date)
        
        # GUID: make unique per app version so RSS readers treat each version as a new item
        SubElement(item, 'guid').text = f"{app_url}#v{latest_version}"
    
    return rss


def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = tostring(elem, encoding='utf-8', xml_declaration=True)
    # Try to prettify, but if it fails, just return the rough string
    try:
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ', encoding='utf-8')
    except Exception as e:
        # If prettifying fails, return un-prettified but valid XML
        print(f"Warning: Could not prettify XML: {e}")
        return rough_string


def generate_rss():
    """Main RSS generation function."""
    print("="*60)
    print("Splunkbase RSS Feed Generator")
    print("="*60)
    print()
    print(f"Configuration:")
    print(f"  PAGES_TO_FETCH: {PAGES_TO_FETCH} {'(all)' if PAGES_TO_FETCH == 0 else ''}")
    print(f"  RSS_MAX_ITEMS: {RSS_MAX_ITEMS}")
    print(f"  OUTPUT_FILE: {OUTPUT_FILE}")
    print()
    
    # Fetch apps
    apps = fetch_latest_apps(max_pages=PAGES_TO_FETCH)
    
    if not apps:
        print("Error: No apps fetched. Exiting.")
        return None
    
    # Generate RSS
    print(f"\nGenerating RSS feed with {min(len(apps), RSS_MAX_ITEMS)} items...")
    rss_root = create_rss_feed(apps, max_items=RSS_MAX_ITEMS)
    
    # Save to file
    xml_content = prettify_xml(rss_root)
    # Ensure each dc:creator has xmlns:dc on the element (ElementTree would output ns2:dc otherwise)
    xml_content = xml_content.replace(
        b'<dc:creator>',
        b'<dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">'
    )
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(xml_content)
    
    print(f"✓ RSS feed saved: {OUTPUT_FILE.absolute()}")
    print()
    
    return OUTPUT_FILE


def main():
    """Main entry point."""
    generate_rss()


if __name__ == "__main__":
    main()
