# TweetsReborn

A static site that turns a Twitter/X archive export into browseable, linkable HTML pages — hosted on GitHub Pages.

**Live site:** https://kerfors.github.io/tweetsreborn/

## Features

- 7,772 original tweets from 2010–2024
- Browse by year and month
- Full-text search (client-side, no server needed)
- Clickable hashtags for tag filtering
- Prev/next navigation between tweets
- Local media (images) served from the repo

## How it works

`generate.py` reads the Twitter archive export in `data/` and generates static HTML into `docs/`, which GitHub Pages serves directly.

```bash
python3 generate.py
```

No dependencies beyond Python 3 standard library.
