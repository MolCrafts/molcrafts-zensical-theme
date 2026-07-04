# MolCrafts Zensical Theme

Shared Zensical theme extension for MolCrafts documentation sites.

## Install

The theme is not on PyPI yet, so consuming sites cannot pin it as a normal
dependency — install it into the same environment that builds the docs:

```bash
pip install -e .
```

> **Note:** because there is no released package, a site's `zensical.toml` can
> reference `theme.name = "molcrafts"` but its `pyproject.toml` cannot yet
> declare the theme in a dependency group. Doc builds therefore depend on this
> package being installed out-of-band (editable install, or once published, a
> version/git pin). Publishing to PyPI would make doc builds reproducible from
> a dependency group alone.

## Use

Add the theme to a Zensical project:

```toml
[project]
site_name = "MolCrafts Project"
site_url = "https://example.molcrafts.org/"

[project.theme]
name = "molcrafts"

[project.extra.molcrafts]
product = "molpy"
accent = "#0284c7"
accent_soft = "rgba(2, 132, 199, 0.14)"
```

All three values are optional. `product` tags the page
(`html[data-molcrafts-product="…"]`) so site or theme CSS can target one
product. `accent` sets the product accent (links, hovers, hero eyebrows);
`accent_soft` is its translucent companion and, when omitted, is derived from
`accent` via `color-mix`. Sites that set none of these fall back to the brand
forest/sand accent. The theme ships no per-product color map — each product
declares its own accent in its `zensical.toml`; the colors the old map used to
assign are kept for reference in a comment at the top of
`assets/stylesheets/molcrafts.css`.

The theme defaults to Zensical's `modern` variant, MolCrafts brand colors from
`moko.svg`, Inter text, JetBrains Mono code, light/dark palettes, navigation
tabs, section indexes, instant navigation, code-copy controls, search
highlighting and suggestions, and TOC following. Consuming sites should not
re-list these `features`/`palette` in their own `zensical.toml` — the theme
already supplies them, and an inline list only risks drifting from the defaults.

## Home page

The theme ships a manual-style landing layout that a stock Zensical site does
not have. It has two parts: a **hero** driven by page front-matter, and a set of
**manual-home components** you compose in Markdown/HTML in the page body.

### Hero (front-matter)

Set a `hero` mapping in the home page's front-matter; the theme's `main.html`
renders it above the content. Every field is optional except that a hero only
renders when the `hero` key is present. The eyebrow above the title is always
"Manual" — it is not configurable.

```yaml
---
title: molpack
hide: [navigation, toc]
hero:
  title: molpack                  # defaults to site_name if omitted
  description: One or two sentences of positioning.
  actions:                        # buttons; style "primary" fills, else outline
    - { label: Get started, href: getting_started/, style: primary }
    - { label: Guide, href: concepts/ }
  install:                        # right-hand card with a copy button;
    label: Install                #   plain string works too, shorthand
    command: pip install molpack  #   for { command: … }
  badges:                         # badge row under the install card
    - img: https://img.shields.io/pypi/v/molpack
      href: https://pypi.org/project/molpack/
      alt: PyPI version
---
```

### Manual-home components (body)

Wrap the body in `.molcrafts-manual-home` and compose these building blocks (all
are plain HTML with `markdown` where inner Markdown is wanted):

| Class | Purpose |
|---|---|
| `molcrafts-manual-section` | A titled row; pair with `molcrafts-manual-section__header` + `molcrafts-manual-eyebrow` |
| `molcrafts-manual-index` | Numbered "find the right page" entry list (`<a><span>01</span><strong>…</strong><em>…</em></a>`) |
| `molcrafts-workflow-list` | Side-labelled `<article>`s, each with a `molcrafts-workflow-list__meta` tag and a code block |
| `molcrafts-feature-matrix` | Two-column `<dl>` of capability `<dt>`/`<dd>` pairs |
| `molcrafts-doc-map` | Grid of `<section><h3>…</h3><p>…</p></section>` linking to nav areas |
| `molcrafts-sr-only` | Visually-hidden `<h1>` so the page still has a heading for a11y/search |

See `examples/basic/docs/index.md` for a complete, copyable example, and the
molpy / molpack `docs/index.md` for production use.

## Local Example

```bash
zensical build -f examples/basic/zensical.toml
zensical serve -f examples/basic/zensical.toml
```

The usage surface is Zensical-native: configure sites with `zensical.toml`.
Zensical 0.0.45 still discovers packaged themes through the historical
`mkdocs.themes` entry point and reads theme-package defaults from
`mkdocs_theme.yml`; this package uses those hooks only for Zensical theme
discovery, not for `mkdocs.yml` configuration.
