# Crutchless

Personal blog. Built with plain HTML, CSS, and a Python build script.

---

## Writing a new post

Create a file in `/posts/` named `YYYY-MM-DD-slug.md`. The date is for sorting; the URL will be `/essays/<slug>.html`.

### Frontmatter

```
---
title: The actual title of the post
date: 2026-05-15
category: joy
excerpt: One sentence shown on index pages.
updated: 2026-05-17
---
```

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Displayed as the page h1 |
| `date` | yes | Publication date, ISO format |
| `category` | yes | Lowercase string; displayed title-cased |
| `excerpt` | no | One sentence; omitted from indexes if absent |
| `updated` | no | Defaults to `date` if absent |

The build script exits with an error if `title`, `date`, or `category` is missing.

---

## Building

```
python publish.py
```

Wipes and rebuilds `dist/` from scratch. Runs in well under a second.
Requires the `markdown` package: `pip install markdown`.

---

## Publishing

```
git add -A
git commit -m "your message"
git push
```

GitHub Pages serves the contents of `/dist` on the `main` branch.
Configure Pages in repo Settings → Pages → Source: `main`, folder: `/dist`.

---

## Images

Drop image files into `/images/`. Reference them in markdown as `![alt](../images/filename.jpg)`.
They are copied to `dist/images/` on each build.
