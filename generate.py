"""
TweetsReborn Static Site Generator
Generates static HTML pages from a Twitter/X archive export.
"""

import json
import os
import shutil
import html
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# --- Configuration ---
ARCHIVE_DIR = "data/twitter-2024-11-20-bf5b9a9210c494d6f71c0d441075f156493fd8a3fbdcc71efdd90ffbf5680b92"
TWEETS_JSON = os.path.join(ARCHIVE_DIR, "data/tweets.json")
MEDIA_SRC = os.path.join(ARCHIVE_DIR, "data/tweets_media")
AVATAR_SRC = os.path.join(ARCHIVE_DIR, "data/profile_media/144624330-Q92DvFtA.jpg")
OUTPUT_DIR = "docs"
MEDIA_OUT = os.path.join(OUTPUT_DIR, "media")

DISPLAY_NAME = "Kerstin Forsberg"
HANDLE = "kerfors"
BIO = "Lifelong Learner and Information Architect caring about clinical trial data and metadata"
LOCATION = "Kungälv, Sweden"

# Set to None to generate all, or a list of IDs for prototyping
PROTOTYPE_IDS = None

# Pinned tweet shown on front page. Set to a tweet ID string, or None to hide.
PINNED_TWEET_ID = "1394956608858427392"


# --- CSS ---
SHARED_CSS = """
:root {
    --bg: #f5f5f0;
    --card-bg: #ffffff;
    --text: #14171a;
    --text-secondary: #536471;
    --accent: #1a8cd8;
    --border: #e0ddd5;
    --hover: #f7f7f2;
    --media-bg: #e8e6df;
    --link: #1a6ba8;
    --font-body: 'Libre Franklin', 'Helvetica Neue', Helvetica, sans-serif;
    --font-display: 'Newsreader', 'Georgia', serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
}

a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }

.container {
    max-width: 620px;
    margin: 0 auto;
    padding: 20px 16px;
}

/* --- Tweet card --- */
.tweet-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    transition: box-shadow 0.15s ease;
}
.tweet-card:hover {
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.tweet-card a.tweet-link {
    color: inherit;
    text-decoration: none;
    display: block;
}
.tweet-card a.tweet-link:hover { text-decoration: none; }

.tweet-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}
.avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    flex-shrink: 0;
}
.author-info { flex: 1; min-width: 0; }
.display-name {
    font-weight: 700;
    font-size: 15px;
    color: var(--text);
}
.handle {
    color: var(--text-secondary);
    font-size: 14px;
}

.tweet-text {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 12px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.tweet-text a { color: var(--accent); }
.tweet-text .hashtag { color: var(--accent); }
.tweet-text .mention { color: var(--accent); }

.tweet-media {
    margin-bottom: 12px;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
}
.tweet-media img {
    width: 100%;
    display: block;
}

.tweet-meta {
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 13px;
    color: var(--text-secondary);
    padding-top: 12px;
    border-top: 1px solid var(--border);
}
.tweet-meta .date { flex: 1; }
.tweet-meta .stat { display: flex; align-items: center; gap: 4px; }
.tweet-meta .stat svg { width: 16px; height: 16px; fill: var(--text-secondary); }

.reply-indicator {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 8px;
}

/* --- Page header --- */
.site-header {
    text-align: center;
    padding: 40px 0 24px;
}
.site-header .avatar {
    width: 72px;
    height: 72px;
    margin: 0 auto 12px;
    display: block;
}
.site-header h1 {
    font-family: var(--font-display);
    font-size: 26px;
    font-weight: 500;
    margin-bottom: 2px;
}
.site-header .handle-line {
    color: var(--text-secondary);
    font-size: 15px;
    margin-bottom: 8px;
}
.site-header .bio {
    color: var(--text-secondary);
    font-size: 14px;
    max-width: 400px;
    margin: 0 auto;
}

/* --- Index pages --- */
.breadcrumb {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 20px;
}
.breadcrumb a { color: var(--text-secondary); }
.breadcrumb a:hover { color: var(--accent); }

.year-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
    margin-top: 20px;
}
.year-card, .month-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.year-card:hover, .month-card:hover {
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-color: var(--accent);
    text-decoration: none;
}
.year-card .year-label, .month-card .month-label {
    font-family: var(--font-display);
    font-size: 22px;
    font-weight: 500;
    color: var(--text);
    display: block;
}
.year-card .count, .month-card .count {
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* --- Pinned tweet --- */
.pinned-section {
    margin: 0 0 28px 0;
}
.pinned-label {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    margin-bottom: 8px;
}
.pinned-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
}
.pinned-text {
    font-size: 15px;
    line-height: 1.55;
    color: var(--text-primary);
    margin-bottom: 12px;
}
.pinned-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 13px;
    color: var(--text-secondary);
}
.pinned-date { flex: 1; }
.pinned-stats { font-weight: 500; }
.pinned-link {
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
}
.pinned-link:hover { text-decoration: underline; }

/* --- Single tweet page --- */
.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 20px;
}
.back-link:hover { color: var(--accent); text-decoration: none; }

.tweet-nav {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
    gap: 12px;
}
.tweet-nav a {
    flex: 1;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    color: var(--text-secondary);
    text-decoration: none;
    transition: border-color 0.15s ease;
}
.tweet-nav a:hover { border-color: var(--accent); color: var(--accent); text-decoration: none; }
.tweet-nav .nav-prev { text-align: left; }
.tweet-nav .nav-next { text-align: right; }
.tweet-nav .nav-label { font-size: 11px; display: block; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; }
.tweet-nav .nav-date { font-size: 13px; display: block; }

.single-tweet .tweet-text {
    font-size: 20px;
    line-height: 1.65;
}

/* --- Search --- */
.search-box {
    display: flex;
    gap: 8px;
    margin: 0 auto 28px;
    max-width: 420px;
}
.search-box input {
    flex: 1;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-family: var(--font-body);
    font-size: 15px;
    background: var(--card-bg);
    color: var(--text);
    outline: none;
}
.search-box input:focus { border-color: var(--accent); }
.search-box button {
    padding: 10px 16px;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: var(--font-body);
    font-size: 15px;
    cursor: pointer;
}
.search-box button:hover { opacity: 0.9; }

.search-result {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: box-shadow 0.15s ease;
}
.search-result:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.search-result a { color: inherit; text-decoration: none; display: block; }
.search-result a:hover { text-decoration: none; }
.search-result .result-text { font-size: 15px; margin-bottom: 6px; }
.search-result .result-date { font-size: 13px; color: var(--text-secondary); }
.search-result mark { background: #fff3b0; border-radius: 2px; }

#search-status { text-align: center; color: var(--text-secondary); font-size: 14px; margin-bottom: 16px; }

/* --- Footer --- */
.site-footer {
    text-align: center;
    padding: 32px 0;
    font-size: 13px;
    color: var(--text-secondary);
    border-top: 1px solid var(--border);
    margin-top: 40px;
}

@media (max-width: 480px) {
    .container { padding: 12px; }
    .tweet-card { padding: 16px; }
    .year-grid { grid-template-columns: repeat(2, 1fr); }
}
"""

HEART_SVG = '<svg viewBox="0 0 24 24"><path d="M20.884 13.19c-1.351 2.48-4.001 5.12-8.379 7.67l-.503.3-.504-.3c-4.379-2.55-7.029-5.19-8.382-7.67-1.36-2.5-1.45-4.55-.334-6.07.93-1.26 2.49-1.99 4.218-1.99 1.13 0 2.24.38 3.12 1.08l.48.38.48-.38c.88-.7 1.99-1.08 3.12-1.08 1.73 0 3.29.73 4.22 1.99 1.11 1.52 1.02 3.57-.34 6.07z"/></svg>'
RT_SVG = '<svg viewBox="0 0 24 24"><path d="M4.5 3.88l4.432 4.14-1.364 1.46L5.5 7.55V16c0 1.1.896 2 2 2H13v2H7.5c-2.209 0-4-1.79-4-4V7.55L1.432 9.48.068 8.02 4.5 3.88zM16.5 6H11V4h5.5c2.209 0 4 1.79 4 4v8.45l2.068-1.93 1.364 1.46-4.432 4.14-4.432-4.14 1.364-1.46 2.068 1.93V8c0-1.1-.896-2-2-2z"/></svg>'


def load_tweets():
    with open(TWEETS_JSON) as f:
        text = f.read().strip()
    # Archive file is missing opening bracket
    data = json.loads('[' + text)
    return data


def parse_date(date_str):
    return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")


def render_tweet_text(tweet, depth=0):
    """Replace entities in full_text with HTML links, working backwards by index."""
    text = tweet['full_text']
    entities = tweet.get('entities', {})
    index_prefix = '../' * depth

    # Collect all entity replacements with their indices
    replacements = []

    for mention in entities.get('user_mentions', []):
        start, end = int(mention['indices'][0]), int(mention['indices'][1])
        name = mention['screen_name']
        link = f'<span class="mention">@{html.escape(name)}</span>'
        replacements.append((start, end, link))

    for url_entity in entities.get('urls', []):
        start, end = int(url_entity['indices'][0]), int(url_entity['indices'][1])
        expanded = url_entity.get('expanded_url', url_entity['url'])
        display = url_entity.get('display_url', expanded)
        link = f'<a href="{html.escape(expanded)}" target="_blank" rel="noopener">{html.escape(display)}</a>'
        replacements.append((start, end, link))

    for hashtag in entities.get('hashtags', []):
        start, end = int(hashtag['indices'][0]), int(hashtag['indices'][1])
        tag = hashtag['text']
        link = f'<a href="{index_prefix}index.html?q=%23{html.escape(tag)}" class="hashtag">#{html.escape(tag)}</a>'
        replacements.append((start, end, link))

    # Remove media URLs from text (they appear at the end)
    for media in entities.get('media', []):
        start, end = int(media['indices'][0]), int(media['indices'][1])
        replacements.append((start, end, ''))

    # Sort by start index descending so replacements don't shift positions
    replacements.sort(key=lambda r: r[0], reverse=True)

    for start, end, replacement in replacements:
        text = text[:start] + replacement + text[end:]

    # Escape remaining plain text parts (but not our HTML)
    # Since we already inserted HTML, we need to be careful
    # The entities handle the escaping for their own parts
    # For plain text between entities, we need to escape &, <, >
    # But since we replaced in-place, we handle it by escaping the original
    # and then doing replacements... let's do it properly:

    # Actually, let's restart with a proper approach
    text = tweet['full_text']
    replacements.sort(key=lambda r: r[0])

    parts = []
    pos = 0
    for start, end, replacement in replacements:
        if start > pos:
            parts.append(html.escape(html.unescape(text[pos:start])))
        parts.append(replacement)
        pos = end
    if pos < len(text):
        parts.append(html.escape(html.unescape(text[pos:])))

    result = ''.join(parts)
    # Convert newlines
    result = result.replace('\n', '<br>')
    return result.strip()


def get_media_html(tweet, depth):
    """Return HTML for media attachments, using local files if available."""
    entities = tweet.get('entities', {})
    extended = tweet.get('extended_entities', {})
    media_list = extended.get('media', entities.get('media', []))
    if not media_list:
        return ''

    prefix = '../' * depth + 'media/'
    parts = []
    for m in media_list:
        tweet_id = tweet['id_str']
        # Check for local file
        media_url = m.get('media_url_https', m.get('media_url', ''))
        filename = media_url.split('/')[-1]
        local_name = f"{tweet_id}-{filename}"
        local_path = os.path.join(MEDIA_SRC, local_name)

        if os.path.exists(local_path):
            parts.append(f'<div class="tweet-media"><img src="{prefix}{local_name}" alt="Tweet media" loading="lazy"></div>')
        elif m.get('type') == 'photo':
            # Fallback to Twitter URL (may break)
            parts.append(f'<div class="tweet-media"><img src="{html.escape(media_url)}" alt="Tweet media" loading="lazy"></div>')

    return '\n'.join(parts)


def format_date_full(dt):
    return dt.strftime("%b %d, %Y · %I:%M %p")


def format_date_short(dt):
    return dt.strftime("%b %d, %Y")


def avatar_path(depth):
    return '../' * depth + 'media/avatar.jpg'


def html_head(title, depth=0):
    css_path = '../' * depth + 'style.css'
    fonts = "https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;700&family=Newsreader:wght@400;500&display=swap"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{css_path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{fonts}" rel="stylesheet">
</head>
"""


def html_footer():
    return f"""<footer class="site-footer">
    Archived tweets from @{HANDLE} · Powered by <a href="https://github.com/kerfors/tweetsreborn">TweetsReborn</a>
</footer>"""


def render_tweet_card(tweet, depth, is_single=False):
    """Render a tweet as an HTML card."""
    dt = parse_date(tweet['created_at'])
    text_html = render_tweet_text(tweet, depth)
    media_html = get_media_html(tweet, depth)
    tweet_id = tweet['id_str']
    favs = int(tweet.get('favorite_count', 0))
    rts = int(tweet.get('retweet_count', 0))

    reply_html = ''
    if tweet.get('in_reply_to_screen_name'):
        reply_to = tweet['in_reply_to_screen_name']
        reply_html = f'<div class="reply-indicator">Replying to <span class="mention">@{html.escape(reply_to)}</span></div>'

    single_class = ' single-tweet' if is_single else ''
    avatar = avatar_path(depth)

    card_inner = f"""
    <div class="tweet-header">
        <img src="{avatar}" alt="{DISPLAY_NAME}" class="avatar">
        <div class="author-info">
            <div class="display-name">{DISPLAY_NAME}</div>
            <div class="handle">@{HANDLE}</div>
        </div>
    </div>
    {reply_html}
    <div class="tweet-text">{text_html}</div>
    {media_html}
    <div class="tweet-meta">
        <span class="date">{format_date_full(dt)}</span>
        <span class="stat">{RT_SVG} {rts}</span>
        <span class="stat">{HEART_SVG} {favs}</span>
    </div>
"""

    if is_single:
        return f'<div class="tweet-card{single_class}">{card_inner}</div>'
    else:
        # Link the whole card to the single tweet page
        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        prefix = '../' * depth
        link = f"{prefix}{year}/{month}/{tweet_id}.html"
        return f'<div class="tweet-card{single_class}"><a href="{link}" class="tweet-link">{card_inner}</a></div>'


def tweet_url(tweet, depth=2):
    dt = parse_date(tweet['created_at'])
    year = dt.strftime('%Y')
    month = dt.strftime('%m')
    return f"{'../' * depth}{year}/{month}/{tweet['id_str']}.html"


def generate_tweet_page(tweet, output_dir, prev_tweet=None, next_tweet=None):
    """Generate a single tweet HTML page."""
    dt = parse_date(tweet['created_at'])
    year = dt.strftime('%Y')
    month = dt.strftime('%m')
    tweet_id = tweet['id_str']

    page_dir = os.path.join(output_dir, year, month)
    os.makedirs(page_dir, exist_ok=True)

    depth = 2  # year/month
    month_name = dt.strftime('%B %Y')

    # Prev/next navigation
    nav_parts = []
    if prev_tweet:
        prev_dt = parse_date(prev_tweet['created_at'])
        nav_parts.append(f'<a href="{tweet_url(prev_tweet, depth)}" class="nav-prev"><div class="nav-label">← Older</div><div class="nav-date">{format_date_short(prev_dt)}</div></a>')
    else:
        nav_parts.append('<span></span>')
    if next_tweet:
        next_dt = parse_date(next_tweet['created_at'])
        nav_parts.append(f'<a href="{tweet_url(next_tweet, depth)}" class="nav-next"><div class="nav-label">Newer →</div><div class="nav-date">{format_date_short(next_dt)}</div></a>')
    else:
        nav_parts.append('<span></span>')
    nav_html = f'<div class="tweet-nav">{"".join(nav_parts)}</div>'

    page_html = html_head(f"@{HANDLE} — {format_date_short(dt)}", depth)
    page_html += f"""<body>
<div class="container">
    <a href="../../{year}/{month}/index.html" class="back-link">← {month_name}</a>
    {render_tweet_card(tweet, depth, is_single=True)}
    {nav_html}
</div>
{html_footer()}
</body>
</html>"""

    filepath = os.path.join(page_dir, f"{tweet_id}.html")
    with open(filepath, 'w') as f:
        f.write(page_html)


def generate_month_index(year, month, tweets, output_dir):
    """Generate month index page listing all tweets in that month."""
    month_name = datetime(int(year), int(month), 1).strftime('%B')
    page_dir = os.path.join(output_dir, year, month)
    os.makedirs(page_dir, exist_ok=True)

    depth = 2
    page_html = html_head(f"@{HANDLE} — {month_name} {year}", depth)
    page_html += f"""<body>
<div class="container">
    <div class="breadcrumb">
        <a href="../../index.html">Archive</a> › <a href="../index.html">{year}</a> › {month_name}
    </div>
    <h2 style="font-family:var(--font-display);font-size:22px;font-weight:500;margin-bottom:20px;">{month_name} {year}</h2>
"""
    # Sort newest first
    tweets_sorted = sorted(tweets, key=lambda t: parse_date(t['created_at']), reverse=True)
    for tweet in tweets_sorted:
        page_html += render_tweet_card(tweet, depth)

    page_html += f"""</div>
{html_footer()}
</body>
</html>"""

    with open(os.path.join(page_dir, 'index.html'), 'w') as f:
        f.write(page_html)


def generate_year_index(year, months_data, output_dir):
    """Generate year index showing months."""
    page_dir = os.path.join(output_dir, year)
    os.makedirs(page_dir, exist_ok=True)

    depth = 1
    page_html = html_head(f"@{HANDLE} — {year}", depth)
    page_html += f"""<body>
<div class="container">
    <div class="breadcrumb">
        <a href="../index.html">Archive</a> › {year}
    </div>
    <h2 style="font-family:var(--font-display);font-size:22px;font-weight:500;margin-bottom:4px;">{year}</h2>
    <div class="year-grid">
"""
    for month_num in sorted(months_data.keys()):
        month_name = datetime(int(year), int(month_num), 1).strftime('%B')
        count = len(months_data[month_num])
        page_html += f"""        <a href="{month_num}/index.html" class="month-card">
            <span class="month-label">{month_name}</span>
            <span class="count">{count} tweet{'s' if count != 1 else ''}</span>
        </a>
"""

    page_html += f"""    </div>
</div>
{html_footer()}
</body>
</html>"""

    with open(os.path.join(page_dir, 'index.html'), 'w') as f:
        f.write(page_html)


def generate_search_index(originals, output_dir):
    """Generate search.json and search.html for client-side search."""
    # Build search index
    index = []
    for tweet in originals:
        dt = parse_date(tweet['created_at'])
        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        tweet_id = tweet['id_str']
        # Plain text for searching (strip HTML entities won't be there yet)
        text = tweet['full_text']
        # Remove media URLs at end of text
        for media in tweet.get('entities', {}).get('media', []):
            text = text[:int(media['indices'][0])] + text[int(media['indices'][1]):]
        # Expand t.co URLs to display URLs
        for url_entity in tweet.get('entities', {}).get('urls', []):
            text = text.replace(url_entity['url'], url_entity.get('display_url', url_entity['url']))
        index.append({
            'id': tweet_id,
            'text': text.strip(),
            'date': dt.strftime('%b %d, %Y'),
            'url': f'{year}/{month}/{tweet_id}.html',
        })

    # Sort newest first
    index.sort(key=lambda x: x['id'], reverse=True)

    with open(os.path.join(output_dir, 'search.json'), 'w') as f:
        json.dump(index, f, ensure_ascii=False)

    return len(index)


def generate_main_index(years_data, output_dir, total_indexed=0):
    """Generate the main archive index."""
    depth = 0
    total = sum(len(t) for months in years_data.values() for t in months.values())
    all_tweets = [t for months in years_data.values() for tweets in months.values() for t in tweets]
    dates = sorted(parse_date(t['created_at']) for t in all_tweets)
    date_range = f"{dates[0].strftime('%b %Y')} – {dates[-1].strftime('%b %Y')}" if dates else ""

    # Pinned tweet
    pinned_html = ""
    if PINNED_TWEET_ID:
        tweet_map = {t.get('tweet', t)['id_str']: t for t in all_tweets}
        pinned = tweet_map.get(PINNED_TWEET_ID)
        if pinned:
            t = pinned.get('tweet', pinned)
            tid = t['id_str']
            dt = parse_date(t['created_at'])
            date_str = dt.strftime('%b %-d, %Y')
            year, month = dt.year, dt.month
            fav = int(t.get('favorite_count', 0))
            rt = int(t.get('retweet_count', 0))
            text = render_tweet_text(t, depth=0)
            url = f"{year}/{month:02d}/{tid}.html"
            pinned_html = f"""    <section class="pinned-section">
        <div class="pinned-label">📌 Pinned tweet</div>
        <div class="pinned-card">
            <div class="pinned-text">{text}</div>
            <div class="pinned-meta">
                <span class="pinned-date">{date_str}</span>
                <span class="pinned-stats">🔁 {rt} &nbsp; ♥ {fav}</span>
                <a href="{url}" class="pinned-link">Read →</a>
            </div>
        </div>
    </section>"""

    page_html = html_head(f"@{HANDLE} — Tweet Archive", depth)
    page_html += f"""<body>
<div class="container">
    <div class="site-header">
        <img src="media/avatar.jpg" alt="{DISPLAY_NAME}" class="avatar">
        <h1>{DISPLAY_NAME}</h1>
        <div class="handle-line">@{HANDLE} · {LOCATION}</div>
        <div class="bio">{html.escape(BIO)}</div>
    </div>
    <p style="text-align:center;color:var(--text-secondary);font-size:14px;margin-bottom:16px;">
        {total} original tweets · {date_range}
    </p>
    <div class="search-box">
        <input type="search" id="q" placeholder="Search {total_indexed} tweets…">
        <button onclick="doSearch()">Search</button>
    </div>
    <div id="search-status"></div>
    <div id="results"></div>
{pinned_html}
    <div id="year-grid" class="year-grid">
"""
    for year in sorted(years_data.keys(), reverse=True):
        count = sum(len(t) for t in years_data[year].values())
        page_html += f"""        <a href="{year}/index.html" class="year-card">
            <span class="year-label">{year}</span>
            <span class="count">{count} tweet{'s' if count != 1 else ''}</span>
        </a>
"""

    page_html += f"""    </div>
</div>
{html_footer()}
<script>
let data = null;

async function loadData() {{
    if (data) return data;
    const r = await fetch('search.json');
    data = await r.json();
    return data;
}}

function highlight(text, query) {{
    if (!query) return text;
    const escaped = query.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    return text.replace(new RegExp(escaped, 'gi'), m => '<mark>' + m + '</mark>');
}}

async function doSearch() {{
    const q = document.getElementById('q').value.trim();
    const status = document.getElementById('search-status');
    const results = document.getElementById('results');
    const grid = document.getElementById('year-grid');

    if (q.length < 2) {{
        status.textContent = '';
        results.innerHTML = '';
        grid.style.display = '';
        document.querySelector('.pinned-section').style.display = '';
        return;
    }}

    const tweets = await loadData();
    const ql = q.toLowerCase();
    const matches = tweets.filter(t => t.text.toLowerCase().includes(ql));

    grid.style.display = 'none';
    document.querySelector('.pinned-section').style.display = 'none';
    status.textContent = matches.length === 0
        ? 'No results.'
        : matches.length + ' result' + (matches.length !== 1 ? 's' : '');

    results.innerHTML = matches.map(t => `
        <div class="search-result">
            <a href="${{t.url}}">
                <div class="result-text">${{highlight(t.text, q)}}</div>
                <div class="result-date">${{t.date}}</div>
            </a>
        </div>`).join('');
}}

document.getElementById('q').addEventListener('input', doSearch);
document.getElementById('q').addEventListener('keydown', e => {{
    if (e.key === 'Escape') {{ e.target.value = ''; doSearch(); }}
}});

// Auto-search from URL parameter (e.g. ?q=%23CDISC from hashtag links)
const urlQ = new URLSearchParams(window.location.search).get('q');
if (urlQ) {{
    document.getElementById('q').value = urlQ;
    doSearch();
}}
</script>
</body>
</html>"""

    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(page_html)


def main():
    print("Loading tweets...")
    all_data = load_tweets()

    # Filter: original tweets only (no RTs)
    originals = [d['tweet'] for d in all_data if not d['tweet'].get('full_text', '').startswith('RT @')]
    print(f"Total tweets: {len(all_data)}, Original: {len(originals)}")

    # Prototype filter
    if PROTOTYPE_IDS:
        originals = [t for t in originals if t['id_str'] in PROTOTYPE_IDS]
        print(f"Prototype mode: {len(originals)} tweets selected")

    # Organize by year/month
    years_data = defaultdict(lambda: defaultdict(list))
    for tweet in originals:
        dt = parse_date(tweet['created_at'])
        years_data[dt.strftime('%Y')][dt.strftime('%m')].append(tweet)

    # Copy media
    os.makedirs(MEDIA_OUT, exist_ok=True)
    shutil.copy2(AVATAR_SRC, os.path.join(MEDIA_OUT, 'avatar.jpg'))
    print("Copied avatar")

    # Copy tweet media for selected tweets
    tweet_ids = {t['id_str'] for t in originals}
    media_count = 0
    for fname in os.listdir(MEDIA_SRC):
        tid = fname.split('-')[0]
        if tid in tweet_ids:
            shutil.copy2(os.path.join(MEDIA_SRC, fname), os.path.join(MEDIA_OUT, fname))
            media_count += 1
    print(f"Copied {media_count} media files")

    # Write shared CSS
    with open(os.path.join(OUTPUT_DIR, 'style.css'), 'w') as f:
        f.write(SHARED_CSS)

    # Generate individual tweet pages (sorted chronologically for prev/next)
    sorted_tweets = sorted(originals, key=lambda t: parse_date(t['created_at']))
    for i, tweet in enumerate(sorted_tweets):
        prev_tweet = sorted_tweets[i - 1] if i > 0 else None
        next_tweet = sorted_tweets[i + 1] if i < len(sorted_tweets) - 1 else None
        generate_tweet_page(tweet, OUTPUT_DIR, prev_tweet, next_tweet)
    print(f"Generated {len(originals)} tweet pages")

    # Generate month indexes
    for year, months in years_data.items():
        for month, tweets in months.items():
            generate_month_index(year, month, tweets, OUTPUT_DIR)

    # Generate year indexes
    for year, months in years_data.items():
        generate_year_index(year, months, OUTPUT_DIR)

    # Generate search index
    total_indexed = generate_search_index(originals, OUTPUT_DIR)

    # Generate main index (needs total_indexed for placeholder text)
    generate_main_index(years_data, OUTPUT_DIR, total_indexed)

    print(f"Done! Open {OUTPUT_DIR}/index.html to preview")


if __name__ == '__main__':
    main()
