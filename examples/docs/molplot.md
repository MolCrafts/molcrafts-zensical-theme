---
title: MolPlot formatter
description: Embed interactive scientific charts with a concise fenced block.
---

# MolPlot formatter

Write a Vega-Lite specification in a `molplot` fenced block. The formatter
turns it into the MolPlot Web Component at build time, so documentation authors
never need to write HTML or JavaScript.

## Conformer energy landscape

[Figure 1](#fig-conformer-landscape) combines continuous position scales, an
energy colour scale, population-sized points, cluster shapes, and rich hover
tooltips. Drag inside the chart to pan, use the mouse wheel over an axis to zoom
that axis, use `shift+wheel` to zoom both axes, and `double-click` to reset.

<figure id="fig-conformer-landscape" class="molcrafts-figure">
<div class="molcrafts-figure__body molcrafts-figure__body--chart" markdown>

```molplot preset="molplot" theme="auto"
mark:
  type: point
  filled: true
  opacity: 0.82
  stroke: white
  strokeWidth: 0.7
data:
  values:
    - {id: conf-01, pc1: -2.8, pc2:  1.8, energy: 0.8, population: 42, cluster: folded}
    - {id: conf-02, pc1: -2.4, pc2:  1.2, energy: 1.1, population: 35, cluster: folded}
    - {id: conf-03, pc1: -2.1, pc2:  2.3, energy: 1.5, population: 27, cluster: folded}
    - {id: conf-04, pc1: -1.7, pc2:  0.7, energy: 2.0, population: 18, cluster: folded}
    - {id: conf-05, pc1: -1.3, pc2: -0.8, energy: 2.7, population: 14, cluster: intermediate}
    - {id: conf-06, pc1: -0.8, pc2: -1.4, energy: 3.2, population: 11, cluster: intermediate}
    - {id: conf-07, pc1: -0.4, pc2: -0.5, energy: 2.5, population: 19, cluster: intermediate}
    - {id: conf-08, pc1:  0.1, pc2: -1.9, energy: 3.8, population: 8,  cluster: intermediate}
    - {id: conf-09, pc1:  0.5, pc2:  0.2, energy: 2.9, population: 16, cluster: intermediate}
    - {id: conf-10, pc1:  1.0, pc2:  1.1, energy: 3.6, population: 10, cluster: open}
    - {id: conf-11, pc1:  1.4, pc2:  1.8, energy: 4.1, population: 7,  cluster: open}
    - {id: conf-12, pc1:  1.8, pc2:  0.5, energy: 3.4, population: 12, cluster: open}
    - {id: conf-13, pc1:  2.2, pc2:  2.4, energy: 4.8, population: 5,  cluster: open}
    - {id: conf-14, pc1:  2.6, pc2: -0.3, energy: 4.3, population: 6,  cluster: open}
    - {id: conf-15, pc1:  3.0, pc2:  1.3, energy: 5.2, population: 4,  cluster: open}
encoding:
  x:
    field: pc1
    type: quantitative
    title: Principal component 1
    scale: {zero: false}
  y:
    field: pc2
    type: quantitative
    title: Principal component 2
    scale: {zero: false}
  color:
    field: energy
    type: quantitative
    title: Relative energy (kcal/mol)
    scale: {scheme: viridis, reverse: true}
  size:
    field: population
    type: quantitative
    title: Population (%)
    scale: {range: [45, 420]}
  shape:
    field: cluster
    type: nominal
    title: State
  tooltip:
    - {field: id, type: nominal, title: Conformer}
    - {field: cluster, type: nominal, title: State}
    - {field: energy, type: quantitative, title: Energy, format: ".1f"}
    - {field: population, type: quantitative, title: Population, format: ".0f"}
```

</div>
<figcaption>
  <span class="molcrafts-figure__label">Figure 1.</span>
  Conformer energy landscape: points coloured by relative energy, sized by
  population, and shaped by conformational state.
</figcaption>
</figure>

## Authoring syntax

The source is just a fenced YAML block:

````markdown
```molplot preset="molplot" theme="auto"
mark: point
data:
  values:
    - {x: 1, y: 2}
    - {x: 2, y: 5}
encoding:
  x: {field: x, type: quantitative}
  y: {field: y, type: quantitative}
```
````

| Fence option | Values | Default |
|---|---|---|
| `preset` | `molplot`, `molplot-paper` | `molplot` |
| `theme` | `auto`, `light`, `dark` | `auto` |
| `aspect` | `16:10`, `4:3`, `16:9`, `W:H` | `16:10` |
| `width` | CSS length | host default (~36rem max) |
| `type` | Chart type hint forwarded to MolPlot | (unset) |

The formatter accepts YAML or JSON. MolPlot supplies the preset, layout, and
default interaction; the fenced body remains a portable Vega-Lite specification.
