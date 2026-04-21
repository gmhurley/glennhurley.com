# glennhurley.com

Personal website for Glenn Hurley, hosted as a static site on GitHub Pages.

## Current State

- Static HTML and CSS
- No build step
- Site content served from `docs/`
- Includes a homepage, log, gallery, and simple browser games

## Structure

- `docs/` - published site files
- `docs/index.html` - homepage
- `docs/log/index.html` - log feed
- `docs/gallery/index.html` - gallery
- `docs/games/` - games landing page
- `docs/hangman/` - hangman game
- `docs/tictactoe/` - tic-tac-toe game
- `docs/css/` - site stylesheets
- `docs/feed.xml` - RSS feed for log entries
- `datadump/` - local scratch space for session files, not for commits

## Future Direction

The site is intentionally simple today. Likely next steps are:

- Expanding the public writing and log sections
- Adding more project or creative work showcases
- Introducing backend or authenticated features only when the static-first approach stops being enough
