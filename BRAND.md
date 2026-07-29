# MolCrafts brand contract

Shared between **molcrafts-zensical-theme** (docs) and **molcrafts-index** (marketing).

## Anchors

| Token | Hex | Role |
|-------|-----|------|
| forest | `#18432b` | Brand primary (headers, links base) |
| forest-light | `#2a6744` | Interactive / hover |
| forest-dark | `#0e2b1b` | Deep chrome |
| cream | `#fbf6e4` | Docs paper (light) |
| sand | `#f2da9d` | Secondary accent |
| sand-strong | `#c8841d` | Warm emphasis |
| slate | `#101811` | Docs dark paper |

## Surfaces

| Surface | Light | Dark |
|---------|-------|------|
| Docs (theme) | cream paper, forest chrome | slate paper, sand accents |
| Marketing (index) | cream-tinted UI, forest buttons | slate-aligned zinc, forest primary |

Cyan (`#1fc0f1` / `#03a3d7`) is a **display spark** only (hero gradients, glows) — not primary buttons.

## Product accents

Declared per product in `zensical.toml`:

```toml
[project.extra.molcrafts]
product = "molpy"
accent = "#0284c7"
accent_soft = "rgba(2, 132, 199, 0.14)"
```

Index product pages use `src/lib/productAccents.ts` with the same hue families.

## Radius

`0.4rem` base — print-manual corners on both sides (not blob SaaS).

## Deploy

| Package | How it ships |
|---------|----------------|
| molcrafts-index | Cloudflare Pages project `index` → `molcrafts.org` (branch `master` on `MolCrafts/index`) |
| molcrafts-zensical-theme | PyPI + GitHub tag `v*`; product docs sites on Cloudflare Pages pull the wheel |
