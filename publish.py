#!/usr/bin/env python3
import os
import sys
import re
import shutil
import json
import time
from datetime import date as date_cls, datetime

try:
    import markdown
except ImportError:
    sys.exit("Error: 'markdown' package not installed. Run: pip install markdown")

DIST = "dist"
POSTS_DIR = "posts"
TEMPLATE_FILE = "template.html"
STYLES_SRC = "styles.css"
IMAGES_SRC = "images"
CHRONOLOGY_FILE = "chronology.json"
TAGLINE = "On leaving behind old gods in favor of a better life."

_md = markdown.Markdown(extensions=["extra", "smarty"])


def render_md(text):
    _md.reset()
    return _md.convert(text)


def parse_frontmatter(text):
    """Return (meta dict, body str). Frontmatter is optional."""
    if not text.startswith("---"):
        return {}, text
    rest = text[3:]
    end = rest.find("\n---")
    if end == -1:
        return {}, text
    meta = {}
    for line in rest[:end].strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    body = rest[end + 4:].lstrip("\n")
    return meta, body


def load_template():
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        return f.read()


def render_page(template, title, content, current=None, depth=0):
    """Inject tokens and fix absolute paths to be relative at the given depth."""
    prefix = "../" * depth
    html = (template
        .replace("{{title}}", title)
        .replace("{{content}}", content)
        .replace("{{nav_essays}}", 'class="current"' if current == "essays" else "")
        .replace("{{nav_about}}", 'class="current"' if current == "about" else "")
        .replace('href="/"', f'href="{prefix}index.html"')
        .replace('href="/styles.css"', f'href="{prefix}styles.css"')
        .replace('href="/essays/"', f'href="{prefix}essays/index.html"')
        .replace('href="/about.html"', f'href="{prefix}about.html"')
    )
    return html


def write_file(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def post_list_html(posts, slug_prefix):
    """Build a <ul class="post-list">. slug_prefix is prepended to each slug.html link."""
    if not posts:
        return "<p>No posts yet.</p>"
    items = []
    for p in posts:
        excerpt = (f'\n      <p class="post-excerpt">{p["excerpt"]}</p>'
                   if p.get("excerpt") else "")
        items.append(
            f'  <li>\n'
            f'    <p class="post-title">'
            f'<a href="{slug_prefix}{p["slug"]}.html">{p["title"]}</a></p>\n'
            f'    <p class="post-meta">{p["published"]}'
            f'<span class="category">{p["category"].title()}</span></p>'
            f'{excerpt}\n'
            f'  </li>'
        )
    return '<ul class="post-list">\n' + "\n".join(items) + "\n</ul>"


def main():
    start = time.time()
    template = load_template()
    today = date_cls.today().isoformat()

    # 1. Wipe and recreate dist/
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "essays"))

    # 2. Copy styles.css and suppress Jekyll
    shutil.copy(STYLES_SRC, os.path.join(DIST, STYLES_SRC))
    open(os.path.join(DIST, ".nojekyll"), "w").close()

    # 3. Copy images/ if present
    if os.path.exists(IMAGES_SRC):
        shutil.copytree(IMAGES_SRC, os.path.join(DIST, "images"))

    # 4. Read and process posts
    POST_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}-(.+)\.md$')
    posts = []
    for filename in sorted(os.listdir(POSTS_DIR)):
        match = POST_PATTERN.match(filename)
        if not match:
            if filename.endswith(".md"):
                print(f"Warning: skipping {filename} (expected YYYY-MM-DD-slug.md)")
            continue
        source = os.path.join(POSTS_DIR, filename)
        with open(source, encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)

        for field in ("title", "date", "category"):
            if field not in meta:
                sys.exit(f"Error: '{field}' missing in frontmatter of {source}")

        slug = match.group(1)
        output_path = os.path.join(DIST, "essays", f"{slug}.html")

        post = {
            "slug": slug,
            "title": meta["title"],
            "category": meta["category"],
            "excerpt": meta.get("excerpt", ""),
            "published": meta["date"],
            "last_edited": meta.get("updated", meta["date"]),
            "source": source.replace("\\", "/"),
            "output": output_path.replace("\\", "/"),
        }

        # Render individual post page
        meta_line = (
            f'<p class="post-meta">{post["published"]}'
            f'<span class="category">{post["category"].title()}</span></p>'
        )
        content = (
            f'<div class="post-header">'
            f'<h1>{post["title"]}</h1>'
            f'{meta_line}'
            f'</div>'
            f'{render_md(body)}'
        )
        write_file(output_path, render_page(template, post["title"], content, depth=1))
        posts.append(post)

    # Sort descending by published date
    posts.sort(key=lambda p: p["published"], reverse=True)

    # 5. Build about page
    with open("about.md", encoding="utf-8") as f:
        about_raw = f.read()
    about_meta, about_body = parse_frontmatter(about_raw)
    about_last_edited = about_meta.get("updated", today)
    about_content = render_md(about_body)
    write_file(
        os.path.join(DIST, "about.html"),
        render_page(template, "About — Crutchless", about_content, current="about", depth=0),
    )

    # 6. Build home page
    home_content = (
        f'<p class="home-wordmark">Crutchless</p>'
        f'<p class="home-tagline">{TAGLINE}</p>'
        f'{post_list_html(posts[:4], slug_prefix="essays/")}'
    )
    write_file(
        os.path.join(DIST, "index.html"),
        render_page(template, "Crutchless", home_content, depth=0),
    )

    # 7. Build essays index
    essays_content = (
        f'<h1 class="page-heading">Essays</h1>'
        f'{post_list_html(posts, slug_prefix="")}'
    )
    write_file(
        os.path.join(DIST, "essays", "index.html"),
        render_page(template, "Essays — Crutchless", essays_content, current="essays", depth=1),
    )

    # 8. Build category indexes
    categories = {}
    for p in posts:
        categories.setdefault(p["category"], []).append(p)

    for cat, cat_posts in categories.items():
        cat_content = (
            f'<h1 class="page-heading">{cat.title()}</h1>'
            f'{post_list_html(cat_posts, slug_prefix="../")}'
        )
        write_file(
            os.path.join(DIST, "essays", cat, "index.html"),
            render_page(template, f"{cat.title()} — Crutchless", cat_content, current="essays", depth=2),
        )

    # 9. Write chronology.json
    chronology = {
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "posts": [
            {
                "slug": p["slug"],
                "title": p["title"],
                "category": p["category"],
                "excerpt": p["excerpt"],
                "published": p["published"],
                "last_edited": p["last_edited"],
                "source": p["source"],
                "output": p["output"],
            }
            for p in posts
        ],
        "about": {"last_edited": about_last_edited},
    }
    with open(CHRONOLOGY_FILE, "w", encoding="utf-8") as f:
        json.dump(chronology, f, indent=2)

    # 10. Summary
    elapsed_ms = int((time.time() - start) * 1000)
    print(f"{len(posts)} posts, {len(categories)} categories, built in {elapsed_ms}ms")


if __name__ == "__main__":
    main()
