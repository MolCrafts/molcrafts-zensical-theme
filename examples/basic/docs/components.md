---
title: Components
hide:
  - toc
hero:
  kicker: Theme pieces
  title: Components
  description: A compact fixture for checking the MolCrafts Zensical theme across hero, content, code, and manual-home components.
  actions:
    - label: Primitives
      href: "#zensical-primitives"
      style: primary
    - label: Manual components
      href: "#manual-homepage-components"
  install:
    label: Package
    methods:
      - label: pip
        command: pip install molcrafts-zensical-theme
      - label: uv
        command: uv add --dev molcrafts-zensical-theme
      - label: source
        command: pip install -e .
  badges:
    - img: https://img.shields.io/badge/theme-molcrafts-0284c7
      href: https://github.com/MolCrafts
      alt: MolCrafts theme
---

<h1 class="molcrafts-sr-only">Components</h1>

## Component catalog

This page keeps the theme's reusable pieces in one place so changes to the
visual system can be checked quickly.

## Zensical primitives

[Primary action](../){ .md-button .md-button--primary }
[Secondary action](../){ .md-button }

!!! note
    The theme keeps Zensical's standard authoring features and only changes the
    MolCrafts visual layer.

!!! tip
    Product accents can be changed per site without editing the theme package.

??? example "Details block"
    Details use the same surface treatment as admonitions, with a compact
    border and product-colored accent.

| Token | Value | Use |
|---|---|---|
| Primary | `#18432B` | Header, footer, and default brand controls |
| Surface | `#FBF6E4` | Light mode document background |
| Accent | `#0284C7` | Product-level links and highlights |

=== "Python"

    ```python
    import molpy as mp

    mol = mp.parser.parse_molecule("CCO")
    ```

=== "Rust"

    ```rust
    use molrs::prelude::*;

    let system = System::default();
    ```

## Manual homepage components

<div class="molcrafts-manual-home" markdown>

<section class="molcrafts-manual-section molcrafts-manual-section--compact" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Index</span>

## Manual index

A numbered entry list for the top of a product manual.

</div>

<nav class="molcrafts-manual-index" aria-label="Component index example">
  <a href="#workflow-list">
    <span>01</span>
    <strong>Workflow list</strong>
    <em>Use side labels and compact code samples for representative paths.</em>
  </a>
  <a href="#feature-matrix">
    <span>02</span>
    <strong>Feature matrix</strong>
    <em>Pair a subsystem name with a short capability description.</em>
  </a>
  <a href="#card-grids">
    <span>03</span>
    <strong>Card grids</strong>
    <em>Show linked guide cards in two or three columns.</em>
  </a>
  <a href="#doc-map">
    <span>04</span>
    <strong>Documentation map</strong>
    <em>Mirror a larger navigation tree in a scan-friendly block.</em>
  </a>
</nav>

</section>

<section id="workflow-list" class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Workflow</span>

## Workflow list

Use this for repeatable paths that need a short explanation and code.

</div>

<div class="molcrafts-workflow-list" markdown>

<article markdown>

<div class="molcrafts-workflow-list__meta">Path 01</div>

### Parse

Create a molecular object from a compact string representation.

```python
mol = mp.parser.parse_molecule("CCO")
frame = mol.to_frame()
```

</article>

<article markdown>

<div class="molcrafts-workflow-list__meta">Path 02</div>

### Type

Attach force-field parameters while keeping the data model explicit.

```python
typed = typifier.typify(mol)
mp.io.write_lammps_system("out/", typed.to_frame(), ff)
```

</article>

</div>

</section>

<section id="feature-matrix" class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Matrix</span>

## Feature matrix

Use this for dense capability summaries.

</div>

<dl class="molcrafts-feature-matrix">
  <div>
    <dt>Parser</dt>
    <dd>SMILES, SMARTS, BigSMILES, and related molecular descriptions.</dd>
  </div>
  <div>
    <dt>Builder</dt>
    <dd>Linear, branched, cyclic, and sampled polymer construction.</dd>
  </div>
  <div>
    <dt>Exporter</dt>
    <dd>LAMMPS, GROMACS, PDB, XYZ, JSON, HDF5, and trajectory formats.</dd>
  </div>
</dl>

</section>

<section id="card-grids" class="molcrafts-manual-section molcrafts-manual-section--stack" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Grid</span>

## Card grids

Stacked sections give card grids the full content width.

</div>

<div class="molcrafts-manual-grid molcrafts-manual-grid--cols-3">
  <a href="../">
    <strong>Build</strong>
    <em>Assemble systems from atoms, residues, and polymer parts.</em>
  </a>
  <a href="../">
    <strong>Type</strong>
    <em>Assign OPLS-AA, GAFF, or custom SMARTS-based parameters.</em>
  </a>
  <a href="../">
    <strong>Export</strong>
    <em>Write simulation-ready files and analysis artifacts.</em>
  </a>
</div>

</section>

<section class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">List</span>

## Manual list

Use this when a numbered index would be too heavy.

</div>

<div class="molcrafts-manual-list">
  <a href="../">
    <strong>parser</strong>
    <em>Turn chemistry strings into structured molecular objects.</em>
  </a>
  <a href="../">
    <strong>builder</strong>
    <em>Grow repeatable molecular and polymer systems.</em>
  </a>
  <a href="../">
    <strong>compute</strong>
    <em>Run analysis routines on frames and trajectories.</em>
  </a>
</div>

</section>

<section id="doc-map" class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Map</span>

## Documentation map

Use this as a compact mirror of a larger navigation tree.

</div>

<div class="molcrafts-doc-map">
  <section>
    <h3>Getting Started</h3>
    <p>Installation, quickstart, examples, and glossary pages.</p>
  </section>
  <section>
    <h3>Concepts</h3>
    <p>Representations, frames, boxes, force fields, and selectors.</p>
  </section>
  <section>
    <h3>Guides</h3>
    <p>Parsing, building, typing, packing, exporting, and analysis workflows.</p>
  </section>
  <section>
    <h3>API Reference</h3>
    <p>Core modules, adapters, engines, wrappers, and compute APIs.</p>
  </section>
</div>

</section>

</div>

## Hero metadata

The homepage hero is rendered from front matter. The `kicker` field is optional
and defaults to `Manual`.

```yaml
hero:
  kicker: Manual
  title: MolPy
  description: Build, edit, type, and export molecular systems.
  actions:
    - { label: Get started, href: "#", style: primary }
    - { label: API reference, href: "#" }
  install:
    methods:
      - label: pip
        command: pip install molpy
      - label: uv
        command: uv add molpy
      - label: source
        command: pip install -e .
  badges:
    - img: https://img.shields.io/pypi/v/molpy
      href: https://pypi.org/project/molpy/
      alt: PyPI version
```
