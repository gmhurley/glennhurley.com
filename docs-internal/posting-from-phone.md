# Posting to the log from your phone

This repo can publish a new log entry from an iOS Shortcut. You type the text;
an iPhone Shortcut sends it to GitHub, a GitHub Action formats it into both
`docs/log/index.html` and `docs/feed.xml`, commits, and GitHub Pages redeploys.

Location and time are filled in automatically by the Shortcut.

> This folder (`docs-internal/`) is notes for you and is **not** part of the
> published site — only `docs/` is served.

## One-time setup

### 1. Create a fine-grained access token

1. GitHub → Settings → Developer settings → **Fine-grained tokens** → *Generate new token*.
2. **Repository access:** Only select repositories → `gmhurley/glennhurley.com`.
3. **Permissions → Repository permissions → Actions:** *Read and write*.
   (That's the only permission needed — it lets the token start the workflow.)
4. Set an expiration you're comfortable with and generate it. Copy the token
   (starts with `github_pat_…`); you won't see it again.

### 2. Build the Shortcut

Create a new Shortcut (name it e.g. "Post to log") with these actions:

1. **Get Current Location**
2. **Get Details of Locations** → *City* → save as variable `City`
3. **Get Details of Locations** → *State* → save as variable `State`
4. **Get Details of Locations** → *Region* → save as variable `Region`
   (Shortcuts has no "Country" field; *Region* returns the country/area name,
   e.g. "Malta".)
5. **If** `State` *has any value*
   - **Text:** `City, State` → set variable `Location`
   - **Otherwise:** **Text:** `City, Region` → set variable `Location`
6. **Format Date** → input *Current Date*, format **ISO 8601**, *Include Time* on,
   include the time zone → save as variable `When`
7. **Ask for Input** (Text) → prompt "What's the post?" → save as variable `Post`
8. **Get Contents of URL**:
   - **URL:** `https://api.github.com/repos/gmhurley/glennhurley.com/actions/workflows/add-log.yml/dispatches`
   - **Method:** `POST`
   - **Headers:**
     - `Authorization` → `Bearer github_pat_YOUR_TOKEN_HERE`
     - `Accept` → `application/vnd.github+json`
   - **Request Body:** JSON. In Shortcuts' field builder, add these — **type
     keys and values without quotation marks**; Shortcuts adds the quotes. (If a
     key shows up as `"ref"` with quotes baked in, GitHub rejects it with a 422
     "not permitted keys" error.)
     - `ref` (Text) → `main`
     - `inputs` (Dictionary) with three Text fields:
       - `text` → *Post* variable
       - `location` → *Location* variable
       - `datetime` → *When* variable

     The assembled body is equivalent to:
     ```json
     { "ref": "main", "inputs": { "text": "...", "location": "...", "datetime": "..." } }
     ```

Add it to your Home Screen or the Share Sheet. A successful call returns
**HTTP 204** with an empty body — that's normal, the post is on its way.

### 3. Watch it land

The Action runs in ~20–40s and pushes a commit. GitHub Pages then redeploys,
so the post is live on glennhurley.com/log a minute or two after you tap.

## Notes

- You can also run it from a laptop: GitHub → **Actions → Add log entry → Run
  workflow**, or locally with
  `python3 scripts/add_log.py --text "..." --location "..." --datetime "2026-06-17T22:45:00+02:00"`.
- The script keeps the log HTML and RSS feed in sync and auto-suffixes the
  entry id (`-b`, `-c`, …) when you post more than once on the same day.
- If `datetime` is left blank the script falls back to the server's UTC clock,
  so it's best to always send the Shortcut's `When` value.
- HTML is escaped automatically, so `<`, `>`, and `&` in a post are safe.
