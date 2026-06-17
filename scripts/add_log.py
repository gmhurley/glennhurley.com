#!/usr/bin/env python3
"""Insert a new log entry into docs/log/index.html and docs/feed.xml.

Designed to be called from a GitHub Action so posts can be added from a phone:
the caller supplies plain text, a location, and an ISO 8601 timestamp, and this
script produces the matching HTML article and RSS <item>, keeping the two files
in sync (see AGENTS.md for the hand-authored format this mirrors).
"""
from __future__ import annotations

import argparse
import html
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "docs" / "log" / "index.html"
FEED_PATH = ROOT / "docs" / "feed.xml"

SITE_URL = "https://glennhurley.com"
DEFAULT_LOCATION = "Winston-Salem, NC"

LOCATION_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C8.13 2 5 5.13 5 9c0 '
    "5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 "
    '2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'
)
SHARE_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.59l5.7 5.7-1.41 1.42L13 '
    "6.41V16h-2V6.41l-3.3 3.3-1.41-1.42L12 2.59zM21 15l-.02 3.51c0 1.38-1.12 2.49-2.5 "
    "2.49H5.5C4.11 21 3 19.88 3 18.5V15h2v3.5c0 .28.22.5.5.5h12.98c.28 0 .5-.22.5-.5L19 "
    '15h2z"/></svg>'
)


def parse_when(raw: str | None) -> datetime:
    """Parse an ISO 8601 timestamp into a timezone-aware datetime."""
    if not raw:
        return datetime.now(timezone.utc)
    text = raw.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.replace(second=0, microsecond=0)


def next_entry_id(html_text: str, when: datetime) -> str:
    """Return the article id for `when`, appending b/c/d... on date collisions."""
    base = f"{when:%Y-%m-%d}"
    existing = re.findall(rf'id="{re.escape(base)}([a-z]?)"', html_text)
    if not existing:
        return base
    return f"{base}{chr(ord('a') + len(existing))}"


def display_time(when: datetime) -> str:
    return f"{when:%-I:%M %p} &middot; {when:%b %-d, %Y}"


def first_sentence(text: str) -> str:
    """Short RSS title: first sentence, or the whole thing if it's brief."""
    match = re.search(r"^(.*?[.!?])(\s|$)", text, re.S)
    title = match.group(1) if match else text
    title = " ".join(title.split())
    return title if len(title) <= 100 else title[:97].rstrip() + "..."


def build_article(entry_id: str, when: datetime, text: str, location: str) -> str:
    body = html.escape(text, quote=False)
    return (
        f'        <article class="tweet" id="{entry_id}">\n'
        '          <div class="tweet-avatar"><img src="/avatar.png" alt="Glenn Hurley" /></div>\n'
        '          <div class="tweet-body">\n'
        '            <div class="tweet-meta">\n'
        f'              <time class="tweet-time" datetime="{when:%Y-%m-%dT%H:%M}">{display_time(when)}</time>\n'
        "            </div>\n"
        f'            <p class="tweet-text">{body}</p>\n'
        '            <div class="tweet-actions">\n'
        '              <span class="tweet-location">\n'
        f"                {LOCATION_SVG}\n"
        f"                {html.escape(location, quote=False)}\n"
        "              </span>\n"
        '              <button class="share-btn" aria-label="Share this post">\n'
        f"                {SHARE_SVG}\n"
        "                Share\n"
        "              </button>\n"
        "            </div>\n"
        "          </div>\n"
        "        </article>"
    )


def build_item(entry_id: str, when: datetime, text: str) -> str:
    url = f"{SITE_URL}/log#{entry_id}"
    title = html.escape(first_sentence(text), quote=False)
    description = text.replace("]]>", "]]&gt;")
    pubdate = format_datetime(when)
    return (
        "    <item>\n"
        f"      <title>{title}</title>\n"
        f"      <link>{url}</link>\n"
        f"      <guid>{url}</guid>\n"
        f"      <pubDate>{pubdate}</pubDate>\n"
        f"      <description><![CDATA[{description}]]></description>\n"
        "    </item>"
    )


def insert_article(html_text: str, article: str) -> str:
    """Insert a new article just after the template comment, above real entries."""
    tpl = html_text.find("<!-- TEMPLATE")
    if tpl == -1:
        raise SystemExit("Could not find the <!-- TEMPLATE comment in the log file.")
    close = html_text.find("-->", tpl)
    if close == -1:
        raise SystemExit("Template comment in the log file is not closed.")
    close += len("-->")
    return f"{html_text[:close]}\n\n{article}{html_text[close:]}"


def insert_item(xml_text: str, item: str) -> str:
    """Insert a new RSS item above all existing items, preserving indentation."""
    idx = xml_text.find("    <item>")
    if idx == -1:
        raise SystemExit("Could not find an <item> insertion point in the feed.")
    return f"{xml_text[:idx]}{item}\n\n{xml_text[idx:]}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a log entry to the site.")
    parser.add_argument("--text", required=True, help="Post body text.")
    parser.add_argument("--location", default=DEFAULT_LOCATION, help="City, region/country.")
    parser.add_argument("--datetime", dest="when", default=None, help="ISO 8601 timestamp.")
    args = parser.parse_args()

    text = " ".join(args.text.split("\n"))
    text = re.sub(r"[ \t]+", " ", text).strip()
    if not text:
        raise SystemExit("Refusing to add an empty post.")
    location = args.location.strip() or DEFAULT_LOCATION
    when = parse_when(args.when)

    log_html = LOG_PATH.read_text(encoding="utf-8")
    feed_xml = FEED_PATH.read_text(encoding="utf-8")

    entry_id = next_entry_id(log_html, when)

    log_html = insert_article(log_html, build_article(entry_id, when, text, location))
    feed_xml = insert_item(feed_xml, build_item(entry_id, when, text))

    LOG_PATH.write_text(log_html, encoding="utf-8")
    FEED_PATH.write_text(feed_xml, encoding="utf-8")

    print(f"Added log entry #{entry_id} at {when:%Y-%m-%d %H:%M %z} ({location})")


if __name__ == "__main__":
    main()
