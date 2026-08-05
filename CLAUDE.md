# molcrafts-zensical-theme

Shared Zensical docs theme (Jinja + static CSS/JS). Ships as a **Python wheel** — no React, no npm runtime deps. Product docs pull it via `pip` on Cloudflare Pages builds.

## Stack

Python ≥3.12, Zensical (modern), static CSS/JS, optional mkdocstrings C++ handler. Tests: pytest/tox only.

## Layout

```
src/molcrafts_zensical_theme/templates/
  assets/stylesheets/tokens.css    brand anchors (sync with index brand-tokens.css)
  assets/stylesheets/molcrafts.css @import tokens.css + surface styles
  main.html, mkdocs_theme.yml, partials/
src/mkdocstrings_handlers/cpp/
tests/test_tokens_contract.py
```

## Brand tokens (manual sync)

No npm/build coupling. Keep these **identical**:

| This repo | Sibling |
|-----------|---------|
| `.../stylesheets/tokens.css` | `molcrafts-index/src/styles/brand-tokens.css` |

Edit one → copy entire file to the other. Product accents stay in each site's `zensical.toml` (`[project.extra.molcrafts]`), not in tokens.

Hex anchors live only in `tokens.css` (not re-declared in `molcrafts.css`).

```bash
uv run --extra dev tox -e py   # includes token contract + optional index identity check
```

## Rules

1. Stay Jinja + static assets; never add a React/shadcn runtime.
2. Consumers set `[project.theme] name = "molcrafts"` only; defaults own features/palette.
3. Version in `pyproject.toml`; release with `v*` tag → PyPI workflow.
4. MolVis/MolPlot fences: theme owns Markdown→HTML; runtime WC loads from CDN (see README).
5. **Iron law — product docs do not own visual system CSS.** Hero, manual-home,
   sections, workflow-list, feature-matrix, doc-map, tile-grid, link-list,
   palette, and figures are theme-only. Product `extra.css` is only for that
   product's unique markup (or a one-line size tweak). Shared layout needs a
   second consumer → promote a theme modifier; do not paste CSS into products.
   Documented in README § "Product extra.css — iron law".

## Release

```bash
uv run --extra dev tox -e py
python -m build && twine check dist/*
# after merge: git tag v0.x.y && git push upstream v0.x.y
```
