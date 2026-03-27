# TweetsReborn

A static site generator that turns a Twitter/X archive export into browseable, linkable HTML pages — hosted on GitHub Pages.

**Live site:** https://kerfors.github.io/tweetsreborn/

## Features

- 7,772 original tweets from 2010–2024
- Browse by year and month
- Full-text search (client-side, no server needed)
- Clickable hashtags for tag filtering
- Prev/next navigation between tweets
- Pinned tweet on the front page
- Local media (images) served from the repo

## How it works

`generate.py` reads the Twitter archive export in `data/` and generates static HTML into `docs/`, which GitHub Pages serves directly.

```bash
python3 generate.py
```

No dependencies beyond Python 3 standard library.

## Use it yourself

1. Download your Twitter/X archive (Settings → Your account → Download an archive)
2. Clone this repo and put your archive in `data/`
3. Update the configuration at the top of `generate.py` (name, handle, bio, archive path)
4. Run `python3 generate.py`
5. Push `docs/` to GitHub and enable GitHub Pages (Settings → Pages → main, /docs)

## Background

Built as a personal project to preserve and browse a Twitter archive after leaving Twitter/X in 2023. The idea was to give old tweets a permanent, readable home — no platform dependency, no account needed to read them.
