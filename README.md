# MolCrafts Zensical Theme

Shared Zensical theme extension for MolCrafts documentation sites.

## Install

```bash
pip install molcrafts-zensical-theme
```

Consuming sites should pin the theme in the dependency group that builds their
docs so builds stay reproducible:

```toml
[dependency-groups]
docs = [
  "zensical>=0.0.45",
  "molcrafts-zensical-theme>=0.2.3",
]
```

For theme development, install the checkout in editable mode instead
(`pip install -e .`).

The distribution includes the MolCrafts C++ handler for `mkdocstrings`; a
second Python package is not required. Rendering C++ API documentation still
requires the `doxygen` executable to be available on `PATH`.

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
For a normal documentation site, setting `name = "molcrafts"` is the complete
visual setup: typography, both color modes, component colors, and navigation
behavior are owned by the theme. Product accent settings and the home-page
components below are optional customization, not required theme tokens.

## Web Component fences (MolVis + MolPlot) — one model

MolVis and MolPlot use the **same ownership split** so docs sites only depend
on this theme (+ zensical):

| Layer | Owner | What you install |
|---|---|---|
| Build-time fence (Markdown → HTML) | **this theme** | `pip install molcrafts-zensical-theme` |
| Run-time Web Component | npm package on CDN (or staged `node_modules`) | nothing in Python |

```toml
extra_javascript = [
  { path = "https://cdn.jsdelivr.net/npm/@molcrafts/molvis-core@latest/dist/elements.js", type = "module" },
  { path = "https://cdn.jsdelivr.net/npm/@molcrafts/molplot@latest/dist/elements.js", type = "module" },
]

[project.markdown_extensions.pymdownx.superfences]
custom_fences = [
  { name = "mermaid", class = "mermaid" },
  { name = "molvis", class = "molvis", format = "molcrafts_zensical_theme.formatters.molvis_fence" },
  { name = "molvis-gallery", class = "molvis-gallery", format = "molcrafts_zensical_theme.formatters.molvis_gallery_fence" },
  { name = "molplot", class = "molplot", format = "molcrafts_zensical_theme.formatters.molplot_fence", validator = "molcrafts_zensical_theme.formatters.molplot_validator" },
]
```

**MolVis:** `format="xyz"` etc.; gallery accepts `src`, `representations`,
`rotation-speed`. **MolPlot:** fence body is a Vega-Lite spec (YAML or JSON);
header options `preset` / `theme` / `width` / `aspect` (default **`4:3`**).
In docs the theme caps chart width (~36rem) and `@molcrafts/molplot` scales
type with container width so paper-preset fonts stay readable on screen.

Local staging (optional): when
`node_modules/@molcrafts/molvis-core` or `node_modules/@molcrafts/molplot` is
present, the formatters copy `dist/` into `docs/assets/{molvis-core,molplot}/`.
Overrides: `MOLVIS_ELEMENTS_DIR`, `MOLPLOT_ELEMENTS_DIR`,
`MOLCRAFTS_DOCS_ASSET_DIR`. Monorepo-relative `core/dist` paths are never used.

The paper-charting Python package (`molcrafts-molplot`) does **not** ship a
Markdown fence — docs sites must use this theme.

### Figure cards (MolVis / MolPlot embeds)

One framed card holds the canvas and a journal-style caption underneath.
Put the viewer/chart first, a `Figure N.` label in the chin, and an `id` for
cross-references (no product chip):

```html
<figure id="fig-water" class="molcrafts-figure">
  <div class="molcrafts-figure__body">
    <molvis-viewer format="xyz" …>…</molvis-viewer>
  </div>
  <figcaption>
    <span class="molcrafts-figure__label">Figure 1.</span>
    Water molecule (ball-and-stick).
  </figcaption>
</figure>
```

In prose, link with Markdown: `[Figure 1](#fig-water)`. Legacy class
`.molcrafts-web-component-card` maps to the same card look.

## Math (arithmatex + MathJax)

The theme enables `navigation.instant`, so MathJax must re-typeset after every
client-side page swap. The theme injects the MathJax config (arithmatex
`processHtmlClass`) and a `document$` re-typeset hook automatically. Sites
only need the library itself:

```toml
extra_javascript = [
  "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
]

[project.markdown_extensions.pymdownx]
arithmatex = { generic = true }
```

Load the MathJax CDN **after** other `extra_javascript` entries (or at least
after any script that might set `window.MathJax`). No separate config file is
required unless you override `main.html`.


## C++ API reference

Enable the bundled handler in the consuming project's `zensical.toml`:

```toml
[project.plugins.mkdocstrings]
default_handler = "cpp"

[project.plugins.mkdocstrings.handlers.cpp]
input = ["include"]
file_patterns = ["*.h", "*.hpp", "*.cpp"]
build_dir = ".cache/mkdocstrings-cpp"

[project.plugins.mkdocstrings.handlers.cpp.options]
show_root_heading = true
members_order = "source"
separate_signature = true
```

Then use normal mkdocstrings directives in Markdown:

```markdown
::: my_namespace::MyClass
    options:
      members_order: source
```

## Home page

The theme ships a manual-style landing layout that a stock Zensical site does
not have. It has two parts: a **hero** driven by page front-matter, and a set of
**manual-home components** you compose in Markdown/HTML in the page body.

### Hero (front-matter)

Set a `hero` mapping in the home page's front-matter; the theme's `main.html`
renders it above the content. Every field is optional except that a hero only
renders when the `hero` key is present. The eyebrow above the title defaults to
"Manual" and can be changed with `hero.kicker`.

```yaml
---
title: molpack
hide: [navigation, toc]
hero:
  kicker: Manual
  title: molpack                  # defaults to site_name if omitted
  description: One or two sentences of positioning.
  actions:                        # buttons; style "primary" fills, else outline
    - { label: Get started, href: getting_started/, style: primary }
    - { label: Guide, href: concepts/ }
  install:                        # right-hand card with copyable tabs
    label: Install
    methods:
      - { label: pip, command: pip install molpack }
      - { label: uv, command: uv add molpack }
      - { label: source, command: pip install -e . }
  badges:                         # badge row under the install card
    - img: https://img.shields.io/pypi/v/molpack
      href: https://pypi.org/project/molpack/
      alt: PyPI version
---
```

For a single install command, the old shorthand still works:

```yaml
hero:
  install:
    command: pip install molpack
```

### Manual-home components (body)

Wrap the body in `.molcrafts-manual-home` and compose these building blocks (all
are plain HTML with `markdown` where inner Markdown is wanted):

| Class | Purpose |
|---|---|
| `molcrafts-manual-section` | A titled row; pair with `molcrafts-manual-section__header` + `molcrafts-manual-eyebrow` |
| `molcrafts-manual-index` | Numbered "find the right page" entry list (`<a><span>01</span><strong>…</strong><em>…</em></a>`) |
| `molcrafts-manual-grid` | Responsive card grid; add `--cols-2` or `--cols-3` (see templates below) |
| `molcrafts-manual-list` | Vertical row list of `label`/`description` pairs (lighter than `manual-index`) |
| `molcrafts-workflow-list` | Side-labelled `<article>`s, each with a `molcrafts-workflow-list__meta` tag and a code block |
| `molcrafts-feature-matrix` | Two-column `<dl>` of capability `<dt>`/`<dd>` pairs |
| `molcrafts-doc-map` | Grid of `<section><h3>…</h3><p>…</p></section>` linking to nav areas |
| `molcrafts-sr-only` | Visually-hidden `<h1>` so the page still has a heading for a11y/search |

See `examples/docs/index.md` for a complete, copyable example, and the
molpy / molpack `docs/index.md` for production use.

### Section templates

A section is built from two orthogonal, opt-in choices so a sub-manual picks a
layout instead of relying on grid auto-placement. Pick a **frame** (how the
titled block splits its label from its content) and drop a **content template**
(how the items inside are arranged) into it.

**Frames** — modifiers on `molcrafts-manual-section`:

| Modifier | Layout |
|---|---|
| *(none)* | Two columns: a sticky label column beside the content |
| `--compact` | Two columns with a static label; a trailing paragraph stacks under the label while the content (e.g. a code block) spans the second column |
| `--stack` | Single column: eyebrow + title on top, content full width below — use to host wide content or a three-column grid |

**Content templates** — drop one into a frame's body (or straight into
`molcrafts-manual-home`):

| Template | Arrangement |
|---|---|
| `molcrafts-manual-grid molcrafts-manual-grid--cols-2` | Two-column card grid → one column on narrow screens |
| `molcrafts-manual-grid molcrafts-manual-grid--cols-3` | Three-column card grid → two, then one |
| `molcrafts-manual-list` | Vertical list of rows |
| `molcrafts-manual-index` | Numbered entry list |

Each card / row is an `<a>` (link, with accent hover) or a `<div>`, holding a
`<strong>` label and an `<em>` or `<p>` description. A three-column grid needs
the room a `--stack` frame gives it:

```html
<section class="molcrafts-manual-section molcrafts-manual-section--stack" markdown>
  <div class="molcrafts-manual-section__header" markdown>
    <span class="molcrafts-manual-eyebrow">Capabilities</span>
    ## What molpy gives you
  </div>
  <div class="molcrafts-manual-grid molcrafts-manual-grid--cols-3">
    <a href="build/"><strong>Build</strong><em>Assemble systems from parts.</em></a>
    <a href="type/"><strong>Type</strong><em>Assign force-field parameters.</em></a>
    <a href="export/"><strong>Export</strong><em>Write LAMMPS, GROMACS, PDB.</em></a>
  </div>
</section>
```

## Local Example

```bash
zensical build -f examples/zensical.toml
zensical serve -f examples/zensical.toml
```

The usage surface is Zensical-native: configure sites with `zensical.toml`.
Zensical 0.0.45 still discovers packaged themes through the historical
`mkdocs.themes` entry point and reads theme-package defaults from
`mkdocs_theme.yml`; this package uses those hooks only for Zensical theme
discovery, not for `mkdocs.yml` configuration.
