# Blog Content

Add one Markdown file per blog post in this directory.

Required frontmatter:

```yaml
---
title: My Post Title
date: 2026-04-20T21:00:00-04:00
slug: my-post-title
description: Short summary for the blog index and RSS.
draft: false
---
```

Optional frontmatter:

```yaml
updated: 2026-04-22T09:30:00-04:00
```

Supported Markdown in the generator:

- Headings
- Paragraphs
- Links and images
- Lists
- Blockquotes
- Fenced code blocks
- Inline code, bold, and italics

Build with:

```bash
python3 scripts/build_blog.py
```
