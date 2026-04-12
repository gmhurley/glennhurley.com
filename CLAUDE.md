# glennhurley.com

Personal website for Glenn Hurley, hosted on GitHub Pages. Site files live in `docs/`.

## Adding a log entry

When the user says "add a post" or "add a log entry", insert a new entry at the top of the feed in `docs/log/index.html`, directly below the `<!-- TEMPLATE -->` comment block.

Use today's date. Default location is **Winston-Salem, NC** unless the user specifies otherwise.

### Entry format

```html
<article class="tweet" id="YYYY-MM-DD">
  <div class="tweet-avatar">GH</div>
  <div class="tweet-body">
    <div class="tweet-meta">
      <span class="tweet-name">Glenn Hurley</span>
      <span class="tweet-handle">@glennhurley</span>
      <span class="tweet-dot">&middot;</span>
      <time class="tweet-time" datetime="YYYY-MM-DDTHH:MM">H:MM AM/PM &middot; Mon D, YYYY</time>
    </div>
    <p class="tweet-text">Post content here.</p>
    <div class="tweet-actions">
      <span class="tweet-location">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        Winston-Salem, NC
      </span>
      <button class="share-btn" aria-label="Share this post">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.59l5.7 5.7-1.41 1.42L13 6.41V16h-2V6.41l-3.3 3.3-1.41-1.42L12 2.59zM21 15l-.02 3.51c0 1.38-1.12 2.49-2.5 2.49H5.5C4.11 21 3 19.88 3 18.5V15h2v3.5c0 .28.22.5.5.5h12.98c.28 0 .5-.22.5-.5L19 15h2z"/></svg>
        Share
      </button>
    </div>
  </div>
</article>
```

### Rules
- Always ask the user for the current time before adding a post
- Entries go **newest first** — insert above all existing entries
- `id` on the article is `YYYY-MM-DD` (used for shareable anchor links)
- If two posts share the same date, append a letter: `2026-04-11b`, `2026-04-11c`
- Keep post text as the user wrote it — don't rewrite or polish it
- After adding the entry, ask if the user wants to commit and push

## Adding a gallery piece

When the user says "add a piece", "add artwork", or similar, insert a new `<figure>` at the top of the grid in `docs/gallery/index.html`, directly above the `<!-- Add new pieces above this line -->` comment.

Images go in `docs/gallery/img/`. The user will provide the filename.

### Entry format

```html
<figure class="artwork">
  <div class="artwork-frame">
    <img src="img/filename.jpg" alt="Brief description of the piece" loading="lazy" />
  </div>
  <figcaption>
    <span class="artwork-title">Title</span>
    <span class="artwork-date">2026</span>
  </figcaption>
</figure>
```

### Rules
- Entries go **newest first** — insert above all existing entries
- The artist's pseudonym is **Artist A** — never publish her real name
- Title and date are optional — omit or leave empty if the piece is untitled
- Use today's year for the date unless the user specifies otherwise
- Keep any title exactly as the user provides it — don't rewrite or polish it
- After adding the entry, ask if the user wants to commit and push

## Data dump folder

`datadump/` is a local-only scratch folder for dropping in screenshots, images, reference files, or any content needed during a session. Its contents are gitignored and will never be committed.

### Rules
- Remind the user to clean out `datadump/` at the end of each session
- Never commit anything from `datadump/` — only `datadump/.gitkeep` is tracked
- If the user pastes or references a file for context, suggest saving it to `datadump/` first

## Structure

```
docs/
  index.html      — homepage
  log/
    index.html    — the log feed
  gallery/
    index.html    — Artist A's gallery
    img/          — artwork image files
  css/
    styles.css    — homepage styles
    log.css       — log page styles
    gallery.css   — gallery styles
  og.png          — open graph image
  favicon.ico
  robots.txt
  sitemap.xml
  CNAME           — glennhurley.com
```
