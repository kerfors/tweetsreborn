# TweetsReborn — Getting Started with Claude Code

## What's ready

- `generate.py` — complete static site generator, tested with 10 prototype tweets
- `CLAUDE.md` — project context file that Claude Code reads automatically
- Twitter archive data already in the repo

## Step 1: Set up Claude Code on the web

1. Go to **claude.com/code**
2. Connect your GitHub account if not already done
3. Select the **kerfors/tweetsreborn** repository

## Step 2: First session — generate prototype and enable Pages

Paste this as your first task:

```
Look at CLAUDE.md to understand the project. Then:

1. Run `python3 generate.py` to generate the prototype site (10 tweets)
2. Create a `.nojekyll` file in docs/ (empty file, prevents Jekyll processing)
3. Preview a few of the generated HTML files to verify they look correct
4. Commit everything (generate.py, CLAUDE.md, docs/, .nojekyll) to a new branch called "site-generator"
5. Push the branch
```

After this, create a PR and merge it. Then go to repo **Settings → Pages → Source** and set it to deploy from branch `main`, folder `/docs`.

## Step 3: Check the live site

After Pages is enabled, visit: **https://kerfors.github.io/tweetsreborn/**

Navigate around — check year grid, month pages, individual tweet pages. Note what you want to change.

## Step 4: Iterate on design

Start a new Claude Code session with feedback, for example:

```
Look at CLAUDE.md. The site is live at kerfors.github.io/tweetsreborn.
I want to change [whatever you noticed]. Make the changes,
regenerate with the prototype (PROTOTYPE_IDS still set),
and commit to a new branch.
```

## Step 5: Full generation

When you're happy with the layout:

```
In generate.py, set PROTOTYPE_IDS = None to generate all tweets.
Run the generator. This will create ~7,772 tweet pages plus
index pages. Commit to a new branch and push.
```

Note: this will add a lot of files to the repo. The media folder
will be ~84MB (already in the repo under data/).

## Tips for working with Claude Code

- Claude Code reads CLAUDE.md automatically — that's where project context lives
- Each session is independent, so be specific about what you want
- For design iteration: describe what you see and what you want changed
- You can run multiple tasks in parallel (e.g., "fix the footer" + "add RSS feed")
- The diff view lets you review all changes before creating a PR
