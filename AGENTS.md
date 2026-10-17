# glennhurley.com

Personal website for Glenn Hurley, hosted on GitHub Pages. Site files live in `docs/`.

Plain static HTML/CSS/JS: no framework, no package manager, no build step except the blog generator (`scripts/build_blog.py`, stdlib Python only). Pushing to `main` deploys.

The user often works from their phone with voice dictation, so expect misspellings in requests (e.g. "Harley" for "Hurley") and interpret them sensibly.

## Conventions for pages

- Every public page includes the GoatCounter snippet just before `</body>`:
  ```html
  <script data-goatcounter="https://shroomslice.goatcounter.com/count"
          async src="//gc.zgo.at/count.js"></script>
  ```
- Standard pages use `/css/styles.css`, a `<main class="container">`, canonical + description meta tags, and the `&copy; <span id="year"></span> Glenn Hurley` footer. Copy `docs/games/index.html` as a starting point.
- Each section lives in its own folder as `docs/<name>/index.html` so URLs are clean (`/games`, `/hormuz`).
- When adding a new top-level section, link it from the homepage nav in `docs/index.html` and add it to `docs/sitemap.xml`.
- Use root-relative links (`/log`, `/css/styles.css`).

## Adding a log entry

The preferred way is the script, which writes the log HTML and the RSS feed together and handles same-day id suffixes:

```bash
python3 scripts/add_log.py --text "..." --location "Winston-Salem, NC" --datetime "2026-06-17T22:45:00-04:00"
```

The same script runs in the `Add log entry` GitHub Action (`.github/workflows/add-log.yml`), which the user's iPhone Shortcut triggers. Setup notes are in `docs-internal/posting-from-phone.md`. Because those posts are committed by the Action, **always pull before editing the log**.

The rest of this section describes the format the script produces, for hand edits.

When the user says "add a post" or "add a log entry", insert a new entry at the top of the feed in `docs/log/index.html`, directly below the `<!-- TEMPLATE -->` comment block.

Use today's date. Default location is **Winston-Salem, NC** unless the user specifies otherwise.

### Entry format

```html
<article class="tweet" id="YYYY-MM-DD">
  <div class="tweet-avatar">GH</div>
  <div class="tweet-body">
    <div class="tweet-meta">
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
- When the user says "post to Twitter", "tweet this", or similar, treat it as a request to add a log entry - the log is a Twitter clone
- Always ask the user for the current time before adding a post
- After adding the log entry, also add a matching `<item>` to the top of `docs/feed.xml` (below the `<channel>` opening tags, above all other items)

### RSS entry format

```xml
<item>
  <title>First sentence or short summary of the post.</title>
  <link>https://glennhurley.com/log#YYYY-MM-DDx</link>
  <guid>https://glennhurley.com/log#YYYY-MM-DDx</guid>
  <pubDate>Day, DD Mon YYYY HH:MM:00 -0400</pubDate>
  <description><![CDATA[Full post text here.]]></description>
</item>
```

- `pubDate` uses RFC 822 format and Eastern time (-0400 EDT / -0500 EST)
- Any relative links in the description (e.g. `/gallery`) should be absolute (`https://glennhurley.com/gallery`)
- The `id` in the `<link>` and `<guid>` must match the article `id` in the log HTML
- Entries go **newest first** - insert above all existing entries
- `id` on the article is `YYYY-MM-DD` (used for shareable anchor links)
- If two posts share the same date, append a letter: `2026-04-11b`, `2026-04-11c`
- Keep post text as the user wrote it - don't rewrite or polish it
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
- Entries go **newest first** - insert above all existing entries
- The artist's pseudonym is **Artist A** - never publish her real name
- Title and date are optional - omit or leave empty if the piece is untitled
- Use today's year for the date unless the user specifies otherwise
- Keep any title exactly as the user provides it - don't rewrite or polish it
- After adding the entry, ask if the user wants to commit and push

## Adding a blog post

Blog posts are authored in Markdown under `content/blog/` and generated into `docs/blog/`.

### Frontmatter format

```yaml
---
title: My Post Title
date: 2026-04-20T21:00:00-04:00
slug: my-post-title
description: Short summary for the blog index and RSS.
draft: false
updated: 2026-04-22T09:30:00-04:00
---
```

- Required fields: `title`, `date`, `slug`, `description`
- `date` and `updated` must include an explicit timezone offset
- `updated` and `draft` are optional
- Keep the user's title and body wording intact unless they ask for editing help

### Rules
- Add one Markdown file per post in `content/blog/`
- Build the blog with `python3 scripts/build_blog.py`
- Generated output lives in `docs/blog/` and should not be hand-edited
- Blog posts are long-form and separate from the log
- The log RSS feed stays at `docs/feed.xml`; blog RSS lives at `docs/blog/feed.xml`
- After adding or editing a blog post, rebuild the blog and ask if the user wants to commit and push

## Games

Small self-contained browser games, each a single `index.html` with inline CSS and JS. They're listed as cards on `docs/games/index.html`; add a card there when you add a game.

- **Tic-Tac-Toe** (`docs/tictactoe/`): player vs. computer. Its shared leaderboard is stored in a jsonbin.io bin, and the API key is embedded in the client-side JS.
- **Hangman** (`docs/hangman/`): kid-friendly word list, paper-and-sketch style.
- **Strait of Hormuz** (`docs/hormuz/`): a joke game the user vibe-coded about steering an oil tanker up the strait past mines, speedboats, drones, and missiles. There's a boss, the gold battleship USS Manifest Destiny (Golden Edition), which faces down the screen with its guns aimed at the tanker. The left shore changes country as you sail (`COUNTRIES`: Oman, then UAE at 30 nm, then Saudi Arabia at 65 nm) with dashed border lines and a "NOW PASSING" banner; Iran is the whole right shore. Iran fires rocket salvos across to the left shore and US B-2 stealth bombers sweep left to right bombing Iran. Both are pure scenery and never damage the player. Everything is drawn on a `<canvas>` in a 400×720 logical coordinate space; `fitCanvas()` scales the backing store by `devicePixelRatio` so it stays sharp on phones, so always draw in logical units. The finish line is at 100 nm (`FINISH_NM`), and tuning constants sit near the top of the script (`PLAYER_SPD`, `BASE_SCROLL`, `DMG`, `OBS`). Collisions use a capsule along the tanker's length (`hullDist`), so hits anywhere on the hull count. Boats and drones weave around a lane kept clear of both shores (so they can't pin themselves to the coast); boats steer their lane toward the tanker and fire RPGs while ahead of it. Difficulty target: winnable but not easy. Sitting still should sink you early; good dodging should sometimes reach the boss. The start screen has a How to Play panel: its hazard list (`HAZARDS`) draws icons with the real game sprites and reads damage from `DMG`, so keep new hazards in that list. It deliberately doesn't spoil the boss. Music is a chiptune loop synthesized live with Web Audio in the `Music` module (no audio files): D Hijaz melody, 132 bpm, layers added at 30 and 65 nm, fades out on death/boarding. Sound effects (`Music.fx`: hit, sink, whoosh, chime, horn) share its audio context; they're only for things that happen to the player, not the background rockets/bombers. Audio starts on the first tap/key (browser autoplay rules). One sound setting covers music and effects: the SOUND toggle on the start screen and the round button in the middle of the in-game bottom bar (or M) both drive it, and it persists in `localStorage` (`hormuz_muted`). The "Hall of Fallen Tankers" leaderboard is per-browser `localStorage` (`hormuz_lb_v1`). Keep the tone tongue-in-cheek. **Bump `VERSION` (top of the script, shown on the start screen) on every change** so the user can tell on their phone whether a fresh copy loaded; GitHub Pages caches pages for ~10 minutes.

## Data dump folder

`datadump/` is a local-only scratch folder for dropping in screenshots, images, reference files, or any content needed during a session. Its contents are gitignored and will never be committed.

### Rules
- Remind the user to clean out `datadump/` at the end of each session
- Never commit anything from `datadump/` - only `datadump/.gitkeep` is tracked
- If the user pastes or references a file for context, suggest saving it to `datadump/` first

## Structure

```
docs/
  index.html      - homepage
  blog/
    index.html    - blog archive
    feed.xml      - blog RSS feed
  log/
    index.html    - the log feed
  gallery/
    index.html    - Artist A's gallery
    img/          - artwork image files
  games/index.html     - games landing page
  tictactoe/index.html - tic-tac-toe
  hangman/index.html   - hangman
  hormuz/index.html    - Strait of Hormuz
  css/
    styles.css    - homepage styles (shared by most pages)
    log.css       - log page styles
    gallery.css   - gallery styles
    blog.css      - blog styles
  feed.xml        - RSS feed (keep in sync with log entries)
  og.png          - open graph image
  favicon.ico
  robots.txt
  sitemap.xml
  CNAME           - glennhurley.com
content/
  blog/           - Markdown source for blog posts
scripts/
  build_blog.py   - generates docs/blog/ from content/blog/
  add_log.py      - adds a log entry + RSS item (used by the phone Action)
docs-internal/    - private notes for the user, not published
.github/workflows/
  add-log.yml     - workflow_dispatch Action for posting from phone
datadump/         - local scratch, gitignored
```
