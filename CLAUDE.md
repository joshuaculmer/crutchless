# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build

```
python publish.py
```

Wipes and rebuilds `dist/` from scratch. No arguments. Requires `pip install markdown` (the only dependency). Output: `N posts, M categories, built in Xms`.

There are no tests, no linter, and no other build steps.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which runs `publish.py` and deploys `dist/` to GitHub Pages via `actions/deploy-pages`. The `dist/` directory is **not committed** to the repo — it is built entirely in CI.

## Architecture

This is a from-scratch static site generator. No framework, no bundler, no JavaScript.

### Source files (edit these)

- `publish.py` — the entire build pipeline in one file
- `template.html` — shared HTML shell with four tokens: `{{title}}`, `{{content}}`, `{{nav_essays}}`, `{{nav_about}}`
- `styles.css` — single stylesheet, copied verbatim to `dist/`
- `posts/YYYY-MM-DD-slug.md` — posts with required frontmatter (`title`, `date`, `category`)
- `about.md` — no frontmatter required; rendered as a plain page
- `images/` — flat directory, copied recursively to `dist/images/`

### How `publish.py` works

1. Wipes `dist/`, copies `styles.css`, drops `.nojekyll`
2. Reads every `YYYY-MM-DD-slug.md` from `posts/` — files not matching that pattern are skipped with a warning
3. Parses a minimal YAML-ish frontmatter (three-dash delimiters, `key: value` lines — no full YAML parser)
4. Renders markdown with `markdown.Markdown(extensions=["extra", "smarty"])`
5. Injects rendered content into `template.html` via plain string replacement
6. Writes `dist/essays/<slug>.html`, `dist/about.html`, `dist/index.html`, `dist/essays/index.html`, and one `dist/essays/<category>/index.html` per category
7. Writes `chronology.json` at the repo root

### Path handling

All links in generated pages use **relative paths** (no absolute `/` paths). The `render_page()` function takes a `depth` argument (0 = root, 1 = `essays/`, 2 = `essays/<category>/`) and rewrites the template's `/`-prefixed hrefs to the correct relative prefix (`../` per level). Links written inside post markdown bodies are **not** rewritten — authors must use the correct relative path manually.

From a post body (`essays/<slug>.html`, depth 1):
- Another post: `other-slug.html`
- About page: `../about.html`
- Essays index: `../essays/index.html`
- Image: `../images/filename.jpg`

### Design constraints (from spec)

- No JavaScript anywhere in `dist/`
- No CSS framework — stylesheet is hand-written
- No web fonts — Georgia (body) and Trebuchet MS (headings/nav) only
- No additional `markdown` extensions beyond `extra` and `smarty`
- Do not add features not in the spec (RSS, search, comments, pagination, etc.)
