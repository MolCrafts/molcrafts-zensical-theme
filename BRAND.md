# MolCrafts brand tokens

**No React. No npm. Manual sync only.**

## Source files (must be identical)

| Repo | Path |
|------|------|
| zensical-theme | `src/molcrafts_zensical_theme/templates/assets/stylesheets/tokens.css` |
| index | `src/styles/brand-tokens.css` |

When you change one, **copy the whole file** to the other. Zensical does not depend on index (and never will).

## What lives in `tokens.css`

- Hex anchors (`--molcrafts-forest`, cream, sand, slate, …)
- HSL channels for the marketing site (`--molcrafts-*-hsl`)
- Radius + shared shadows

Product accents are **not** here — each docs site sets them in `zensical.toml`:

```toml
[project.extra.molcrafts]
product = "molpy"
accent = "#0284c7"
```

## How each side consumes tokens

| Side | How |
|------|-----|
| Theme | `@import url("tokens.css")` from `molcrafts.css` → shipped in the wheel |
| Index | `@import "./brand-tokens.css"` then map to shadcn HSL UI vars in `tailwind.css` |

## Check drift

From the theme repo (stdlib pytest only):

```bash
uv run --extra dev tox -e py
# includes tests/test_tokens_contract.py
# if ../molcrafts-index exists, also asserts byte-identical tokens
```

## Anchors (quick ref)

| Token | Hex |
|-------|-----|
| forest | `#18432b` |
| forest-light | `#2a6744` |
| forest-dark | `#0e2b1b` |
| cream | `#fbf6e4` |
| sand | `#f2da9d` |
| sand-strong | `#c8841d` |
| slate | `#101811` |
| radius | `0.4rem` |

Cyan (`--molcrafts-cyan-spark`) is display-only, not interactive primary.
