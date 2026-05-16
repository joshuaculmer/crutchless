# Crutchless — Build Spec

## What this is

A personal blog called **Crutchless**, about leaving entertainment addiction behind and replacing it with a deliberate life. The site has three sections: Home, Essays, About. Posts are written in markdown, converted to static HTML by a Python script, and served by GitHub Pages.

Build this in the order given below. Do not add features, dependencies, or polish beyond what is specified. The whole point of the project is restraint — both in the writing and the architecture. If you find yourself reaching for a library, a framework, or a "nice touch," stop and reread this document.

---

## Stack

- **No framework.** No React, no Vite, no Node, no MDX, no bundler, no JavaScript at all on the rendered pages.
- **Plain HTML + CSS** for the served site.
- **Python** for the build script. The only dependency is the `markdown` package (`pip install markdown`). Use Python 3.10+.
- **GitHub Pages** serves the contents of `/dist` on the `main` branch.

If you think something here would be easier or better with another tool, you are wrong for this project. Ship it as specified.

---

## Repo layout

```
crutchless/
  SPEC.md              # this file
  README.md            # short, see below
  publish.py           # the build script
  template.html        # shared layout
  styles.css           # single stylesheet
  chronology.json      # generated state file (committed)
  posts/
    YYYY-MM-DD-slug.md
  about.md
  images/              # flat directory for inline images
  dist/                # generated; what GH Pages serves
    index.html
    about.html
    styles.css
    essays/
      index.html
      <slug>.html
      <category>/
        index.html
    images/
```

The `dist/` directory is committed to the repo. GH Pages config will point at `/dist` on `main`.

---

## Pages

### Home (`dist/index.html`)

- Large "Crutchless" wordmark at the top. Trebuchet, heavy weight, large size. This is the visual anchor of the site.
- One-line tagline beneath the wordmark: *"On leaving behind old gods in favor of a better life."* (Treat this string as final unless told otherwise.)
- Below the tagline, the four most recent essays (by `date` field) regardless of category. Each entry shows:
  - Title (links to the post)
  - Date (small, quiet, beneath the title)
  - Category tag (small uppercase, accent color)
  - Excerpt (one line, only if present in frontmatter)
- Footer with nav links to Essays and About.

### Essays index (`dist/essays/index.html`)

- Heading: "Essays"
- Full reverse-chronological list of every post. Same entry format as the home page: title, date, category tag, excerpt.
- No pagination. The list grows over time and that's fine.

### Category index (`dist/essays/<category>/index.html`)

- Auto-generated for every category that appears in any post's frontmatter.
- Heading: the category name, capitalized (e.g. "Joy", "Struggle").
- Reverse-chronological list of posts in that category only. Same entry format.
- Categories are discovered from posts at build time. Do not hardcode the category list anywhere.

### Post (`dist/essays/<slug>.html`)

- Title (h1)
- Date and category tag beneath the title (small, quiet)
- Rendered markdown body
- Footer with nav links to Essays and About

### About (`dist/about.html`)

- Renders `about.md` into the same layout as a post, but with no date and no category tag in the header.

---

## Post format

Posts live in `/posts/` and are named `YYYY-MM-DD-slug.md`. The URL becomes `/essays/<slug>.html` — the date is dropped from the URL. The date in the filename is for sorting in the file system; the canonical date is the frontmatter `date` field.

Frontmatter:

```yaml
---
title: The actual title of the post
date: 2026-05-15
updated: 2026-05-17     # optional; defaults to date
category: joy           # required; any lowercase string
excerpt: One sentence shown on index pages.  # optional
---
```

Rules:
- `title`, `date`, and `category` are required. If any is missing, the build script exits with a clear error naming the offending file.
- `updated` is optional; if absent, treat it as equal to `date`.
- `excerpt` is optional; if absent, omit it from index pages entirely. Do not auto-generate one from the post body.
- `category` is a lowercase string. The display version is title-cased by the build script (`joy` → `Joy`).

---

## Build script (`publish.py`)

Usage:
```
python publish.py
```

No arguments. Full rebuild every time. Should run in well under a second for a few dozen posts.

Steps, in order:

1. Wipe `dist/` and recreate it.
2. Copy `styles.css` to `dist/styles.css`.
3. Copy `images/` to `dist/images/` (recursive).
4. Read every `.md` file in `posts/`. For each:
   - Parse frontmatter (use a simple YAML-ish parser — three dashes, key-value lines, three dashes; full YAML is overkill, but if you want to use `pyyaml` that's acceptable).
   - Validate required fields.
   - Render the markdown body to HTML using the `markdown` package.
   - Inject into `template.html` and write to `dist/essays/<slug>.html`.
5. Parse `about.md` the same way (no frontmatter required; render the body, inject into template, write to `dist/about.html`).
6. Build the homepage at `dist/index.html` — wordmark, tagline, four most recent posts.
7. Build the Essays index at `dist/essays/index.html` — all posts, reverse chronological.
8. For each unique category found across posts, build `dist/essays/<category>/index.html`.
9. Write `chronology.json` at the repo root (see schema below).
10. Print a summary to stdout: `N posts, M categories, built in Xms`.

### Markdown rendering

Use the `markdown` package with these extensions: `extra`, `smarty`. That gives you footnotes, tables, smart quotes, and em/en dashes. Nothing else.

### Template

`template.html` is a single file with placeholder tokens the script replaces. Use simple string replacement, not a templating engine. Tokens:

- `{{title}}` — page title for the `<title>` tag
- `{{content}}` — the main body HTML
- `{{nav_essays}}`, `{{nav_about}}` — used to mark the current nav link (the script sets these to either an empty string or `class="current"`)

Keep the template small. Header has the wordmark (links to home) and nav (Essays, About). Main is a single column. Footer is a thin line with the nav repeated. That's it.

### chronology.json

Generated on every build. Schema:

```json
{
  "generated_at": "2026-05-15T14:32:00",
  "posts": [
    {
      "slug": "some-title",
      "title": "The actual title",
      "category": "joy",
      "excerpt": "One sentence.",
      "published": "2026-05-15",
      "last_edited": "2026-05-17",
      "source": "posts/2026-05-15-some-title.md",
      "output": "dist/essays/some-title.html"
    }
  ],
  "about": {
    "last_edited": "2026-05-10"
  }
}
```

Posts array is sorted by `published` descending. `about.last_edited` should default to today's date if `about.md` has no frontmatter — but if you add an `updated:` field to `about.md`'s frontmatter, use that. Don't read git history; use frontmatter only.

The chronology file is committed to the repo. It exists so the build script and any future tooling have a single state file to reference.

---

## Design

The design has to feel deliberate and slightly bookish. Reference for *restraint* (not UI): are.na. Nothing decorative. No animations. No hover effects beyond what's required (links). No cards. No shadows. No rounded corners on content. The site should read like printed matter that happens to be online.

### Palette

- Background: `#141c16` (cool dark green)
- Text: `#e8e6df` (warm off-white — NOT pure white, which buzzes against this background)
- Accent: `#84b48e` (sage)
- Muted text (dates, metadata): a slightly dimmed version of the text color — try `#a8a59c` and adjust if needed.

Use accent sparingly. Links, category tags, current-nav indicator, hairline rules. That's it. If you find yourself using the accent for decoration, remove it.

### Typography

- Body: **Georgia**, serif. System font, no webfont loading.
- Headings and wordmark: **Trebuchet MS**, sans-serif.
- Stack: `Georgia, "Times New Roman", serif` and `"Trebuchet MS", "Lucida Sans Unicode", sans-serif`.
- Body size: 18–19px. Line-height around 1.6. Measure (line length) capped around 65–75 characters via `max-width` on the content column.
- The "Crutchless" wordmark on the home page is large — somewhere around 4–5rem. Tagline beneath is sans, regular weight, maybe 1.1rem, in muted text color.
- h1 for post titles. h2 and h3 for in-post structure. Don't use h4+.

### Links

Always underlined. Accent color (`#84b48e`). On hover: same color, underline thickens slightly OR the text gets a touch brighter — pick one, not both. Keep it subtle.

### Layout

- Single content column, centered, `max-width` around 36rem (≈580px).
- Generous vertical rhythm. Don't crowd.
- Header at top: wordmark on the left links to home, nav on the right (Essays, About). On narrow screens, nav drops below the wordmark — no hamburger menu.
- Footer is a thin hairline rule above a small line of nav links, accent color.
- Index page entries are separated by vertical space, not borders or boxes. A small hairline rule between them is acceptable if it doesn't feel busy.

### Category tags

Small, uppercase, accent color, letter-spacing slightly increased. Inline near the date. No background, no border, no pill shape — just the word.

### Images

Inline, full-width within the content column. No captions unless the markdown supplies them. No lightbox. Use the natural `<img>` tag the markdown renderer produces. Lazy-loading via the `loading="lazy"` attribute is acceptable — add it in the build script if straightforward.

### Responsive

The single-column layout means responsiveness is mostly free. Make sure it reads well at 360px wide and at 1400px wide. Don't add breakpoints you don't need.

---

## README.md

Write a short README aimed at me (the author). It should explain:

1. How to write a new post (create a markdown file in `/posts/`, frontmatter format).
2. How to build (`python publish.py`).
3. How to publish (commit and push; GH Pages serves `/dist`).
4. Frontmatter field reference.

Keep it under 80 lines. No badges, no fluff.

---

## Initial content

Create one example post so the build has something to render. Put it in `/posts/` with today's date, category `joy`, and a paragraph or two of placeholder Lorem-replacement content that fits the blog's voice — something like a short reflection on cooking dinner instead of opening a screen. This is a placeholder I will replace; don't make it long.

Create `about.md` with a single-line placeholder ("About page — to be written.").

---

## What "done" looks like

- `python publish.py` runs cleanly with no errors and no warnings.
- `dist/` contains a fully working static site that can be opened directly in a browser (no server required) and looks right.
- The home page shows the wordmark, tagline, and one post (the example).
- The Essays index shows one post.
- The category index at `/essays/joy/` exists and shows one post.
- The example post renders with title, date, category tag, and body.
- The About page renders.
- `chronology.json` exists and matches the schema above.
- All pages share `styles.css`. Changing a color in `styles.css` and rebuilding visibly updates every page.
- No JavaScript files anywhere in `dist/`.
- The site looks restrained, deliberate, and bookish — not like a generic AI-styled landing page.

---

## What to avoid

- Don't add tagging, search, comments, RSS, dark/light toggle, analytics, social share buttons, "subscribe" forms, or any other feature not in this spec.
- Don't reach for a static site generator (Eleventy, Hugo, Astro, Jekyll). The Python script IS the generator.
- Don't use a CSS framework (Tailwind, Bootstrap, anything). Write the CSS by hand. It will be short.
- Don't use Google Fonts or any other webfont service. Georgia and Trebuchet are on every machine.
- Don't add hover animations, transitions longer than 100ms, gradients, drop shadows, glassmorphism, or other contemporary UI tells.
- Don't use emoji in the UI.
- Don't ask the user clarifying questions during the build. The spec is final. If you genuinely hit ambiguity, make the more restrained choice and note it in the README.

---

## Final note

The author of this blog is choosing to live with less. The site should feel that way. Every element should justify its presence. When in doubt: remove it.
