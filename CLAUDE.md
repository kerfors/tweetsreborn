# TweetsReborn

Static site generator that turns a Twitter/X archive export into browseable, linkable HTML pages hosted on GitHub Pages.

## Project structure

```
tweetsreborn/
├── generate.py              # Main generator script (Python 3, no dependencies beyond stdlib)
├── CLAUDE.md                # This file
├── README.md
├── data/
│   └── twitter-2024-11-20-.../   # Raw Twitter archive export
│       ├── data/
│       │   ├── tweets.json       # 14,444 tweets (NOTE: missing opening '[' — parser prepends it)
│       │   ├── tweets_media/     # 614 local media files (jpg/png/mp4, 84MB)
│       │   ├── profile_media/    # Avatar images
│       │   └── *.js              # Other archive data (likes, followers, DMs, etc.)
│       └── Your archive.html     # Twitter's own viewer (not used)
└── docs/                    # Generated output — served by GitHub Pages
    ├── index.html           # Main archive page with year grid
    ├── style.css            # Shared stylesheet
    ├── media/               # Copied avatar + tweet media
    └── {year}/
        ├── index.html       # Year page with month grid
        └── {month}/
            ├── index.html   # Month page with tweet cards (newest first)
            └── {tweet_id}.html  # Individual tweet pages
```

## Key facts about the data

- **14,444 total tweets**, of which **7,772 are originals** (no RTs). Only originals are rendered.
- Date range: April 2017 – November 2024
- `tweets.json` is a JSON array but **missing the opening `[`** — the parser does `json.loads('[' + text)`.
- Tweet entities (mentions, URLs, hashtags, media) have character `indices` for precise in-text replacement.
- Local media filenames follow pattern: `{tweet_id}-{original_filename}.{ext}`
- Profile avatar: `data/profile_media/144624330-Q92DvFtA.jpg`

## Current state

The generator (`generate.py`) is functional with:
- Entity rendering (mentions, URLs, hashtags, media) with correct index-based replacement
- Individual tweet pages at `docs/{year}/{month}/{tweet_id}.html`
- Month index pages with tweet card listings
- Year index pages with month grid
- Main index with year grid
- Twitter-like card layout with warm off-white color scheme
- Google Fonts (Libre Franklin + Newsreader)
- Responsive design
- Local media support with Twitter CDN fallback

Currently running in **prototype mode** (10 selected tweets). Set `PROTOTYPE_IDS = None` in generate.py to generate all 7,772 tweets.

## How to work with this

### Generate the site
```bash
python3 generate.py
```

### Preview locally
```bash
cd docs && python3 -m http.server 8000
# Open http://localhost:8000
```

### Generate all tweets (not just prototype)
In `generate.py`, change line 29 to:
```python
PROTOTYPE_IDS = None
```

### Enable GitHub Pages
In repo Settings → Pages → Source: Deploy from branch `main`, folder `/docs`.
The site will be at: `https://kerfors.github.io/tweetsreborn/`

## Code conventions

- Python 3, standard library only (json, os, shutil, html, datetime, collections, pathlib)
- 4-space indentation
- All HTML is self-contained with relative paths (no absolute URLs except Google Fonts)
- CSS uses custom properties for easy theming
- Media paths use `'../' * depth + 'media/'` pattern for correct relative references at any nesting level

## What NOT to change without asking

- The `tweets.json` parsing workaround (missing `[`)
- The entity replacement logic (index-based, must process backwards or collect-and-rebuild)
- The `docs/` output directory (GitHub Pages depends on it)
- Archive data files under `data/` (read-only source data)

## Next steps / ideas

- [ ] Full generation (all 7,772 tweets)
- [ ] Verify layout and styling in browser, iterate on design
- [ ] Add .nojekyll file to docs/ (prevents GitHub Pages Jekyll processing)
- [ ] Update README.md with project description and site link
- [ ] Consider: reply threads, search, tag filtering, RSS feed
