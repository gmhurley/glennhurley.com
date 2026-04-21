---
title: Mac Clipboard Screenshots on Linux
date: 2026-04-20T22:55:00-04:00
slug: recreating-macos-clipboard-screenshots-on-linux
description: How to recreate macOS-style clipboard screenshots on Linux with a single Flameshot shortcut.
draft: false
---

One of the most underrated macOS features is this shortcut:

**`Cmd + Ctrl + Shift + 4`**

On my Linux box, I mapped the same shortcut pattern to:

**`Alt + Ctrl + Shift + 4`**

It lets you:

- Select an area of the screen
- Instantly copy it to your clipboard
- Paste it anywhere (Slack, email, docs, etc.)

No files. No cleanup. Just fast.

When I moved back to Linux, this was the one thing I missed the most.

So I recreated it with the same keys and same feel. The only real change is swapping macOS's `Cmd` key for Linux's `Alt` key.

## The Goal

I wanted a single shortcut on Linux that:

- Lets me drag to select part of the screen
- Copies directly to the clipboard
- Doesn’t save a file
- Feels instant and frictionless

Same idea, same key pattern, just adapted for Linux.

## The Tool: Flameshot

Flameshot makes this possible with one command:

```bash
flameshot gui -c
```

What this does:

- Opens the selection UI
- Lets you drag to capture
- Automatically copies the result to your clipboard

That `-c` flag is the key.

## Step 1: Install Flameshot

On Debian/Ubuntu/Pop!_OS:

```bash
sudo apt install flameshot
```

## Step 2: Create the Shortcut

Go to:

Settings → Keyboard → View and Customize Shortcuts

Scroll down and add a **custom shortcut**.

## Step 3: Add Your Mac-Style Binding

Set:

- **Name:** Screenshot to Clipboard
- **Command:**

```bash
flameshot gui -c
```

- **Shortcut:**
Set it to **`Alt + Ctrl + Shift + 4`**

## What I Used

To keep the shortcut as close as possible to macOS, I used:

**`Alt + Ctrl + Shift + 4`**

Why?

- Linux doesn’t have `Cmd`
- `Alt` is the closest stand-in for that position in the shortcut
- The rest of the keys stay exactly the same

## Step 4: Test It

Press your shortcut.

You should get:

- A crosshair cursor
- Click and drag to select
- Release → screenshot is already in your clipboard

Now just hit paste (`Ctrl + V`) anywhere.

## The Result

This gets you almost the exact same shortcut on both systems:

| Action | macOS | Linux (with Flameshot) |
| ------ | ----- | ---------------------- |
| Clipboard area screenshot | `Cmd + Ctrl + Shift + 4` | `Alt + Ctrl + Shift + 4` |

## Final Thoughts

Most Linux screenshot tools default to saving files.

That’s fine… until you realize how often you just want to paste something quickly.

This setup removes that friction entirely.

It’s one of those tiny tweaks that ends up saving time *every single day*.

If you’re coming from macOS, this is one shortcut worth recreating first.
