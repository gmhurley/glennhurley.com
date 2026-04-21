#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "blog"
OUTPUT_DIR = ROOT / "docs" / "blog"
FEED_PATH = OUTPUT_DIR / "feed.xml"

SITE_URL = "https://glennhurley.com"
SITE_NAME = "Glenn Hurley"


@dataclass(frozen=True)
class Post:
    source_path: Path
    title: str
    slug: str
    description: str
    date: datetime
    updated: datetime | None
    draft: bool
    body_markdown: str
    body_html: str

    @property
    def output_dir(self) -> Path:
        return OUTPUT_DIR / f"{self.date:%Y}" / f"{self.date:%m}" / self.slug

    @property
    def url_path(self) -> str:
        return f"/blog/{self.date:%Y}/{self.date:%m}/{self.slug}/"

    @property
    def url(self) -> str:
        return f"{SITE_URL}{self.url_path}"

    @property
    def published_display(self) -> str:
        return self.date.strftime("%B %-d, %Y")

    @property
    def published_iso(self) -> str:
        return self.date.date().isoformat()

    @property
    def updated_iso(self) -> str | None:
        return self.updated.date().isoformat() if self.updated else None


def main() -> None:
    posts = load_posts()
    build_output(posts)


def load_posts() -> list[Post]:
    posts: list[Post] = []
    seen_paths: set[str] = set()

    if not CONTENT_DIR.exists():
        return posts

    for path in sorted(CONTENT_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        post = parse_post(path)
        if post.draft:
            continue
        if post.url_path in seen_paths:
            raise ValueError(f"Duplicate generated path for {post.source_path}: {post.url_path}")
        seen_paths.add(post.url_path)
        posts.append(post)

    posts.sort(key=lambda post: post.date, reverse=True)
    return posts


def parse_post(path: Path) -> Post:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw, path)
    title = require_field(frontmatter, "title", path)
    slug = require_field(frontmatter, "slug", path)
    description = require_field(frontmatter, "description", path)
    date = parse_datetime(require_field(frontmatter, "date", path), path, "date")
    updated_raw = frontmatter.get("updated")
    updated = parse_datetime(updated_raw, path, "updated") if updated_raw else None
    draft = frontmatter.get("draft", "").strip().lower() == "true"

    return Post(
        source_path=path,
        title=title,
        slug=slug,
        description=description,
        date=date,
        updated=updated,
        draft=draft,
        body_markdown=body.strip(),
        body_html=render_markdown(body.strip()),
    )


def split_frontmatter(raw: str, path: Path) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        raise ValueError(f"{path} is missing frontmatter")

    parts = raw.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError(f"{path} has invalid frontmatter delimiters")

    frontmatter_text = parts[0][4:]
    body = parts[1]
    frontmatter: dict[str, str] = {}

    for line in frontmatter_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            raise ValueError(f"{path} has invalid frontmatter line: {line}")
        key, value = stripped.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, body


def require_field(frontmatter: dict[str, str], key: str, path: Path) -> str:
    value = frontmatter.get(key, "").strip()
    if not value:
        raise ValueError(f"{path} is missing required field: {key}")
    return value


def parse_datetime(value: str, path: Path, field_name: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{path} has invalid {field_name}: {value}") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{path} {field_name} must include an explicit timezone offset")
    return dt


def render_markdown(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    ordered_items: list[str] = []
    quote_lines: list[str] = []
    table_lines: list[str] = []
    code_lines: list[str] = []
    code_language: str = ""
    in_code = False

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            text = " ".join(line.strip() for line in paragraph_lines)
            blocks.append(f"<p>{render_inline(text)}</p>")
            paragraph_lines = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            items = "".join(f"<li>{render_inline(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
            list_items = []

    def flush_ordered() -> None:
        nonlocal ordered_items
        if ordered_items:
            items = "".join(f"<li>{render_inline(item)}</li>" for item in ordered_items)
            blocks.append(f"<ol>{items}</ol>")
            ordered_items = []

    def flush_quote() -> None:
        nonlocal quote_lines
        if quote_lines:
            content = "\n".join(quote_lines).strip()
            blocks.append(f"<blockquote>{render_markdown(content)}</blockquote>")
            quote_lines = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            blocks.append(render_table(table_lines))
            table_lines = []

    def flush_code() -> None:
        nonlocal code_lines, code_language
        if code_lines:
            language_class = f' class="language-{html.escape(code_language)}"' if code_language else ""
            code = html.escape("\n".join(code_lines))
            blocks.append(f"<pre><code{language_class}>{code}</code></pre>")
            code_lines = []
            code_language = ""

    for line in lines:
        if in_code:
            if line.startswith("```"):
                flush_code()
                in_code = False
            else:
                code_lines.append(line)
            continue

        stripped = line.strip()
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_ordered()
            flush_quote()
            flush_table()
            in_code = True
            code_language = line[3:].strip()
            code_lines = []
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            flush_ordered()
            flush_quote()
            flush_table()
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            flush_ordered()
            flush_table()
            quote_lines.append(stripped[1:].lstrip())
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            flush_ordered()
            flush_quote()
            flush_table()
            level = len(heading_match.group(1))
            blocks.append(f"<h{level}>{render_inline(heading_match.group(2))}</h{level}>")
            continue

        unordered_match = re.match(r"^[-*]\s+(.*)$", stripped)
        if unordered_match:
            flush_paragraph()
            flush_ordered()
            flush_quote()
            flush_table()
            list_items.append(unordered_match.group(1))
            continue

        ordered_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ordered_match:
            flush_paragraph()
            flush_list()
            flush_quote()
            flush_table()
            ordered_items.append(ordered_match.group(1))
            continue

        if is_table_line(stripped):
            flush_paragraph()
            flush_list()
            flush_ordered()
            flush_quote()
            table_lines.append(stripped)
            continue

        flush_list()
        flush_ordered()
        flush_quote()
        flush_table()
        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    flush_ordered()
    flush_quote()
    flush_table()
    if in_code:
        flush_code()

    return "\n".join(blocks)


def is_table_line(line: str) -> bool:
    return "|" in line and line.count("|") >= 2


def split_table_row(line: str) -> list[str]:
    trimmed = line.strip()
    if trimmed.startswith("|"):
        trimmed = trimmed[1:]
    if trimmed.endswith("|"):
        trimmed = trimmed[:-1]
    return [cell.strip() for cell in trimmed.split("|")]


def is_table_separator(line: str, column_count: int) -> bool:
    cells = split_table_row(line)
    if len(cells) != column_count:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def render_table(lines: list[str]) -> str:
    if len(lines) < 2:
        return "".join(f"<p>{render_inline(line)}</p>" for line in lines)

    header_cells = split_table_row(lines[0])
    if not header_cells or not is_table_separator(lines[1], len(header_cells)):
        return "".join(f"<p>{render_inline(line)}</p>" for line in lines)

    body_rows = []
    for line in lines[2:]:
        cells = split_table_row(line)
        if len(cells) != len(header_cells):
            return "".join(f"<p>{render_inline(row)}</p>" for row in lines)
        rendered_cells = "".join(f"<td>{render_inline(cell)}</td>" for cell in cells)
        body_rows.append(f"<tr>{rendered_cells}</tr>")

    header_html = "".join(f"<th>{render_inline(cell)}</th>" for cell in header_cells)
    body_html = "".join(body_rows)
    return (
        '<div class="post-table-wrap"><table><thead><tr>'
        f"{header_html}</tr></thead><tbody>{body_html}</tbody></table></div>"
    )


def render_inline(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"@@PLACEHOLDER{len(placeholders) - 1}@@"

    def image_replace(match: re.Match[str]) -> str:
        alt = html.escape(match.group(1))
        src = html.escape(match.group(2), quote=True)
        return stash(f'<img src="{src}" alt="{alt}" loading="lazy" />')

    def link_replace(match: re.Match[str]) -> str:
        label = html.escape(match.group(1))
        href = html.escape(match.group(2), quote=True)
        return stash(f'<a href="{href}">{label}</a>')

    def code_replace(match: re.Match[str]) -> str:
        return stash(f"<code>{html.escape(match.group(1))}</code>")

    working = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_replace, text)
    working = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_replace, working)
    working = re.sub(r"`([^`]+)`", code_replace, working)
    working = html.escape(working)
    working = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", working)
    working = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", working)

    for index, value in enumerate(placeholders):
        working = working.replace(f"@@PLACEHOLDER{index}@@", value)

    return working


def build_output(posts: Iterable[Post]) -> None:
    posts = list(posts)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for post in posts:
        post.output_dir.mkdir(parents=True, exist_ok=True)
        (post.output_dir / "index.html").write_text(render_post_page(post), encoding="utf-8")

    (OUTPUT_DIR / "index.html").write_text(render_index_page(posts), encoding="utf-8")
    FEED_PATH.write_text(render_feed(posts), encoding="utf-8")


def render_index_page(posts: list[Post]) -> str:
    if posts:
        items = "\n".join(render_index_item(post) for post in posts)
    else:
        items = """
        <article class="blog-empty">
          <h2>No posts yet</h2>
          <p>The blog is live. The first long-form post will land here soon.</p>
          <p>Until then, the <a href="/log">Log</a> is where the shorter updates live.</p>
        </article>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Blog | {SITE_NAME}</title>
  <meta name="description" content="Long-form writing from Glenn Hurley about projects, experiments, and whatever is worth a deeper look." />
  <link rel="canonical" href="{SITE_URL}/blog" />
  <link rel="icon" href="/favicon.ico" />
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} Blog" href="/blog/feed.xml" />
  <link rel="stylesheet" href="/css/blog.css" />
</head>
<body>
  <main class="blog-shell">
    <header class="blog-header">
      <div class="blog-topbar">
        <a class="blog-home" href="/">&larr; glennhurley.com</a>
        <a class="blog-toplink" href="/log">Log</a>
      </div>
      <h1>Blog</h1>
      <p class="blog-intro">Longer posts about projects, experiments, and ideas that need more room than the <a href="/log">Log</a>.</p>
    </header>

    <section class="blog-list" aria-label="Blog posts">
{items}
    </section>

    <footer class="blog-footer">
      &copy; <span id="year"></span> Glenn Hurley
    </footer>
  </main>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();
  </script>
  <script data-goatcounter="https://shroomslice.goatcounter.com/count"
          async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""


def render_index_item(post: Post) -> str:
    return f"""      <article class="post-card">
        <p class="post-card-meta"><time datetime="{post.published_iso}">{html.escape(post.published_display)}</time></p>
        <h2><a href="{post.url_path}">{html.escape(post.title)}</a></h2>
        <p>{html.escape(post.description)}</p>
        <a class="post-card-link" href="{post.url_path}">Read post</a>
      </article>"""


def render_post_page(post: Post) -> str:
    updated_html = ""
    if post.updated_iso:
        updated_display = post.updated.strftime("%B %-d, %Y")
        updated_html = f'<p class="post-updated">Updated <time datetime="{post.updated_iso}">{html.escape(updated_display)}</time></p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(post.title)} | {SITE_NAME}</title>
  <meta name="description" content="{html.escape(post.description, quote=True)}" />
  <link rel="canonical" href="{post.url}" />
  <link rel="icon" href="/favicon.ico" />
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} Blog" href="/blog/feed.xml" />
  <link rel="stylesheet" href="/css/blog.css" />
</head>
<body>
  <main class="post-shell">
    <article class="post">
      <div class="blog-topbar">
        <a class="blog-home" href="/">&larr; glennhurley.com</a>
        <a class="blog-toplink" href="/log">Log</a>
      </div>
      <header class="post-header">
        <p class="post-backlink"><a href="/blog">&larr; Back to Blog</a></p>
        <h1>{html.escape(post.title)}</h1>
        <p class="post-meta"><time datetime="{post.published_iso}">{html.escape(post.published_display)}</time></p>
        {updated_html}
      </header>
      <div class="post-body">
        {post.body_html}
      </div>
    </article>

    <footer class="blog-footer">
      &copy; <span id="year"></span> Glenn Hurley &nbsp;&middot;&nbsp; <a href="/blog/feed.xml">RSS</a>
    </footer>
  </main>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();
  </script>
  <script data-goatcounter="https://shroomslice.goatcounter.com/count"
          async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""


def render_feed(posts: list[Post]) -> str:
    items = "\n".join(render_feed_item(post) for post in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_NAME} Blog</title>
    <link>{SITE_URL}/blog</link>
    <description>Long-form writing from Glenn Hurley.</description>
    <language>en-us</language>
    <atom:link href="{SITE_URL}/blog/feed.xml" rel="self" type="application/rss+xml" />

{items}
  </channel>
</rss>
"""


def render_feed_item(post: Post) -> str:
    description = html.escape(post.description)
    return f"""    <item>
      <title>{html.escape(post.title)}</title>
      <link>{post.url}</link>
      <guid>{post.url}</guid>
      <pubDate>{format_datetime(post.date)}</pubDate>
      <description><![CDATA[{description}]]></description>
    </item>"""


if __name__ == "__main__":
    main()
