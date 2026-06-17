---
title: Posting to My Site From My Phone With an Apple Shortcut
date: 2026-06-18T00:30:00+02:00
slug: posting-to-my-site-from-my-phone
description: How I wired up an Apple Shortcut and a GitHub Action so I can post to my site's log straight from my phone — and the setup headaches I hit along the way.
draft: false
---

My [log](/log) is a little Twitter clone. Short thoughts, timestamps, a location pin — the stuff I miss about old Twitter. The problem: every "tweet" was really me opening a laptop, hand-editing two files, keeping the HTML and the RSS feed in sync, and pushing to GitHub.

That's a lot of friction for a one-line thought. So thoughts stopped getting posted.

I wanted to post from my phone, the way you'd actually use Twitter. Here's what I landed on.

## The Idea

The whole thing is three pieces:

1. **An Apple Shortcut** on my phone — I tap it, it grabs my location and the time, and asks for the text.
2. **A GitHub Action** that takes that text and runs a script.
3. **A Python script** in the repo that formats the post into both the log page and the RSS feed, commits, and lets GitHub Pages redeploy.

The key decision: the phone only sends **plain text**. All the formatting logic lives in the repo, where I can actually test and fix it. The phone has the easy job.

## The Script

The script does the boring, error-prone part — turning a sentence into a properly formatted entry in two places and keeping them in sync. It takes three arguments:

```bash
python3 scripts/add_log.py \
  --text "Back in Malta. Posting this from my phone." \
  --location "Msida, Malta" \
  --datetime "2026-06-18T00:16:00+02:00"
```

It escapes the HTML, builds the RSS `<item>`, and even auto-numbers the entry id when I post more than once in a day. I never touch the markup.

## The GitHub Action

A `workflow_dispatch` workflow runs the script and commits the result:

```yaml
on:
  workflow_dispatch:
    inputs:
      text:
        required: true
      location:
        default: "Winston-Salem, NC"
      datetime:
        default: ""
```

One thing worth doing here: pass the inputs into the script through environment variables, not by dropping them straight into the shell command. Otherwise a stray quote — or a `<script>` tag in a post — can break the run (or worse).

## The Shortcut

This is the part that talks to GitHub. The Shortcut:

- Gets the current location and pulls out **City** and **Region**
- Formats the current date as **ISO 8601** (with the time zone)
- Asks me for the post text
- Sends it all to GitHub's API with **Get Contents of URL**:

```
POST https://api.github.com/repos/<user>/<repo>/actions/workflows/add-log.yml/dispatches
```

With an `Authorization: Bearer <token>` header and a JSON body pointing at the branch and the inputs. A fine-grained token scoped to just this one repo, with **Actions: read and write**, is all it needs.

Tap, type, done. The post is live a minute later.

## The Headaches (So You Can Skip Them)

I won't pretend this was smooth. The script and the Action were quick. The **Shortcut** was the pain. Three things got me:

**1. There's no "Country" field.** Apple's *Get Details of Location* gives you City and State, but no Country. The one you want is **Region** — at the country level it returns the country name (it gave me "Malta").

**2. JSON quotes.** In the Shortcut's request-body builder, you type keys and values *without* quotation marks — it adds them for you. Type `"ref"` with the quotes and GitHub bounces it with a `422 "not permitted keys"` error.

**3. ISO 8601, for real.** My first working dispatch failed because the Shortcut sent `Jun 18, 2026 at 12:12 AM` instead of `2026-06-18T00:12:00+02:00`. The script wants a real ISO timestamp with a time zone offset — otherwise it can't know I'm six time zones from home. Make sure the date is actually formatted, and that the *formatted* value is the one going into the request, not the raw date.

## The Result

| | Before | After |
| --- | --- | --- |
| Where I post from | Laptop | Phone |
| Files I edit by hand | 2 | 0 |
| Steps | Open editor, format HTML, format RSS, commit, push | Tap, type |

Was the Shortcut a pain to set up? Yes. But it's a one-time pain, and now posting a thought is genuinely as easy as it should've been all along.

This very site is static — no database, no server, no CMS. Turns out you don't need one to post from your phone. You just need a shortcut and a little glue.
