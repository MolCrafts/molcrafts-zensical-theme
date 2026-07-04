---
title: MolPy
description: A programmable toolkit for molecular simulation workflows.
hide:
  - navigation
  - toc
hero:
  title: MolPy
  description: A programmable toolkit for molecular simulation workflows. Build, edit, type, and export molecular systems in Python with explicit, composable data structures.
  actions:
    - label: Get started
      href: "#representative-workflows"
      style: primary
    - label: Guides
      href: "#core-capabilities"
    - label: API reference
      href: components/
  install:
    command: pip install molpy
  badges:
    - img: https://img.shields.io/pypi/v/molpy
      href: https://pypi.org/project/molpy/
      alt: PyPI version
    - img: https://img.shields.io/badge/python-3.12%2B-blue
      href: https://pypi.org/project/molpy/
      alt: Python 3.12+
---

<h1 class="molcrafts-sr-only">MolPy</h1>

<div class="molcrafts-manual-home" markdown>

<section class="molcrafts-manual-section molcrafts-manual-section--compact" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Start here</span>

## Find the right page

Use this page as an index into the manual, not a marketing overview.

</div>

<nav class="molcrafts-manual-index" aria-label="Manual entry points">
  <a href="#representative-workflows">
    <span>01</span>
    <strong>Install and verify</strong>
    <em>Set up Python, install MolPy, and run the first parse to export example.</em>
  </a>
  <a href="#core-capabilities">
    <span>02</span>
    <strong>Read the data model</strong>
    <em>Understand Atomistic, Frame, Block, ForceField, and conversion boundaries.</em>
  </a>
  <a href="#representative-workflows">
    <span>03</span>
    <strong>Follow a workflow</strong>
    <em>Move from small molecules and polymer chains to AmberTools-backed preparation.</em>
  </a>
  <a href="components/">
    <span>04</span>
    <strong>Look up API details</strong>
    <em>Open parser, builder, typifier, pack, compute, I/O, engine, and adapter references.</em>
  </a>
</nav>

</section>

<section id="representative-workflows" class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Workflows</span>

## Representative workflows

MolPy workflows share one explicit molecular representation, so examples can
move from construction to typing, packing, and export without hidden state.

</div>

<div class="molcrafts-workflow-list" markdown>

<article markdown>

<div class="molcrafts-workflow-list__meta">Workflow 01</div>

### Small molecule

Parse a molecule from SMILES, assign force-field types, and export simulation
files.

```python
mol = mp.parser.parse_molecule("CCO")
typed = mp.typifier.OplsTypifier(ff).typify(mol)
mp.io.write_lammps_system("output/", typed.to_frame(), ff)
```

</article>

<article markdown>

<div class="molcrafts-workflow-list__meta">Workflow 02</div>

### Polymer chain

Construct a chain from G-BigSMILES notation and carry it through the same data
model.

```python
from molpy.builder import polymer

peo = polymer("{[<]CCOCC[>]}|10|")
packed = mp.pack.pack([peo.to_frame()], box=[80, 80, 80])
```

</article>

<article markdown>

<div class="molcrafts-workflow-list__meta">Workflow 03</div>

### Parameter pipeline

Prepare monomers, invoke external tools, and keep generated topology artifacts
attached to structured results.

```python
eo = PrepareMonomer().run("{[<]CCOCC[>]}")
chain = polymer("{[#EO]|20}", library={"EO": eo}, backend="amber")
```

</article>

</div>

</section>

<section id="core-capabilities" class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Features</span>

## Core capabilities

The manual is organized around subsystems. Each feature below links to a layer
that can be used independently or composed into larger workflows.

</div>

<dl class="molcrafts-feature-matrix">
  <div>
    <dt>Representations</dt>
    <dd>Editable topology graphs, numerical frames, force fields, boxes, and typed conversion boundaries.</dd>
  </div>
  <div>
    <dt>Parsers</dt>
    <dd>SMILES, SMARTS, BigSMILES, CGSmiles, and G-BigSMILES for molecular and polymer descriptions.</dd>
  </div>
  <div>
    <dt>Builders</dt>
    <dd>Linear, branched, cyclic, and polydisperse polymer assembly with reproducible sampling.</dd>
  </div>
  <div>
    <dt>Typifiers</dt>
    <dd>OPLS-AA, GAFF/GAFF2, and custom SMARTS/SMIRKS based atom typing.</dd>
  </div>
  <div>
    <dt>Packing and compute</dt>
    <dd>Packmol-backed packing plus RDF, MSD, clustering, shape, dielectric, and neighbor-list operations.</dd>
  </div>
  <div>
    <dt>I/O and engines</dt>
    <dd>PDB, GRO, LAMMPS, XYZ, JSON, HDF5, force-field files, trajectories, and MD input generation.</dd>
  </div>
</dl>

</section>

<section class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Map</span>

## Documentation map

The sections below mirror the navigation tree so the homepage works as a
compact table of contents for returning users.

</div>

<div class="molcrafts-doc-map">
  <section>
    <h3>Getting Started</h3>
    <p>Installation, quickstart, examples, MCP setup, naming conventions, glossary, and FAQ.</p>
  </section>
  <section>
    <h3>Concepts</h3>
    <p>Atomistic/topology layers, frames, periodic boxes, force fields, trajectories, selectors, wrappers, engines, I/O, and workflow boundaries.</p>
  </section>
  <section>
    <h3>Guides</h3>
    <p>Parsing chemistry, building polymers, crosslinking, polydispersity, force field typification, AmberTools, and Moltemplate CLI.</p>
  </section>
  <section>
    <h3>API Reference</h3>
    <p>Core, parser, reacter, builder, pack, typifier, potential, I/O, adapter, wrapper, engine, optimization, and compute APIs.</p>
  </section>
</div>

</section>

<section class="molcrafts-manual-section molcrafts-manual-section--stack" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Templates</span>

## Three-column card grid

The `--stack` frame gives content the full width, so a `molcrafts-manual-grid`
with `--cols-3` has room to breathe. It steps down to two columns, then one, on
narrower screens.

</div>

<div class="molcrafts-manual-grid molcrafts-manual-grid--cols-3">
  <a href="components/">
    <strong>Build</strong>
    <em>Assemble systems from atoms, residues, and polymer parts.</em>
  </a>
  <a href="components/">
    <strong>Type</strong>
    <em>Assign OPLS-AA, GAFF, or custom SMARTS-based parameters.</em>
  </a>
  <a href="components/">
    <strong>Export</strong>
    <em>Write LAMMPS, GROMACS, PDB, XYZ, and HDF5 outputs.</em>
  </a>
</div>

</section>

<section class="molcrafts-manual-section" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Templates</span>

## Vertical list

`molcrafts-manual-list` pairs a short label with a description and works inside
the default two-column frame.

</div>

<div class="molcrafts-manual-list">
  <a href="components/">
    <strong>parser</strong>
    <em>Turn SMILES, SMARTS, and BigSMILES strings into structures.</em>
  </a>
  <a href="components/">
    <strong>builder</strong>
    <em>Grow linear, branched, and cyclic polymers reproducibly.</em>
  </a>
  <a href="components/">
    <strong>compute</strong>
    <em>Run RDF, MSD, clustering, and neighbor-list analyses.</em>
  </a>
</div>

</section>

</div>
