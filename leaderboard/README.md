# Hormuz global leaderboard

Cloudflare Worker + D1 (SQLite) backing the "GLOBAL TOP 10" tab in
`docs/hormuz/`. Not part of the published site; GitHub Pages only serves `docs/`.

## API

- `GET  /scores` → `{ top: [{ id, name, flag, nm, damage, created_at }] }`
- `POST /scores` with `{ name, flag, nm, damage, durationMs }` →
  `{ top, you: { id, rank, name } }`

The server checks ranges, rejects runs faster than the game's physics allow,
rate-limits each IP (3 s between scores, 100/day), and swaps offensive tanker
names for `MV [REDACTED]`. CORS only allows glennhurley.com.

## Deploy (first time)

```bash
cd leaderboard
npm install
export CLOUDFLARE_API_TOKEN=...          # Workers Scripts:Edit + D1:Edit
npx wrangler d1 create hormuz-leaderboard   # paste the database_id into wrangler.toml
npm run db:init:remote
npx wrangler secret put IP_SALT          # any random string
npm run deploy                            # prints the https://...workers.dev URL
```

Then set `LB_API` in `docs/hormuz/index.html` to that URL.

## Local dev

```bash
npm run db:init:local
npx wrangler dev --port 8799
```

## Admin

```bash
# remove a score
npx wrangler d1 execute hormuz-leaderboard --remote --command "DELETE FROM scores WHERE id = 123"
# see the latest submissions
npx wrangler d1 execute hormuz-leaderboard --remote --command "SELECT id, name, nm, damage, created_at FROM scores ORDER BY id DESC LIMIT 20"
```
