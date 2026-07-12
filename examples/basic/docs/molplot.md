---
title: MolPlot Web Component
description: Render responsive Vega-Lite charts with the MolPlot Web Component.
---

# MolPlot Web Component

`<molplot-chart>` renders a Vega-Lite specification with MolPlot's shared
scientific preset. The chart automatically resizes with its documentation
container.

## Live example

<figure class="molcrafts-web-component-card">
  <figcaption>
    <span class="molcrafts-web-component-card__package">MolPlot</span>
    <strong>Energy profile</strong>
    <small>A responsive Vega-Lite line chart rendered with the MolPlot preset.</small>
  </figcaption>
  <div class="molcrafts-web-component-preview molcrafts-web-component-preview--chart">
    <molplot-chart preset="molplot" theme="light">
      <script type="application/json">
      {
        "mark": {"type": "line", "point": true},
        "data": {
          "values": [
            {"step": 0, "energy": 1.00},
            {"step": 1, "energy": 0.66},
            {"step": 2, "energy": 0.48},
            {"step": 3, "energy": 0.35},
            {"step": 4, "energy": 0.29}
          ]
        },
        "encoding": {
          "x": {"field": "step", "type": "quantitative", "title": "Simulation step"},
          "y": {"field": "energy", "type": "quantitative", "title": "Energy (a.u.)"}
        }
      }
      </script>
    </molplot-chart>
  </div>
</figure>

## Enable the component

Load the ESM bundle once in `zensical.toml`:

```toml
extra_javascript = [
  { path = "https://cdn.jsdelivr.net/npm/@molcrafts/molplot@latest/dist/elements.js", type = "module" },
]
```

## Parameters

| Attribute | Values | Default | Description |
|---|---|---|---|
| `preset` | `molplot`, `molplot-paper` | `molplot` | Shared screen or publication preset. |
| `theme` | `auto`, `light`, `dark` | `auto` | Chart color mode. |
| `spec` | One-line JSON | — | Inline Vega-Lite spec when a script child is inconvenient. |

The recommended source is a child `<script type="application/json">`, which
keeps multiline JSON readable and avoids escaping it into an attribute.

## Script-based specification

```html
<molplot-chart preset="molplot" theme="light">
  <script type="application/json">
  {
    "mark": "point",
    "data": {
      "values": [
        {"x": 1, "y": 2},
        {"x": 2, "y": 5},
        {"x": 3, "y": 4}
      ]
    },
    "encoding": {
      "x": {"field": "x", "type": "quantitative"},
      "y": {"field": "y", "type": "quantitative"}
    }
  }
  </script>
</molplot-chart>
```

## Attribute specification

For a short, single-line specification, use the `spec` attribute:

```html
<molplot-chart
  preset="molplot-paper"
  theme="light"
  spec='{"mark":"bar","data":{"values":[{"group":"A","value":4},{"group":"B","value":7}]},"encoding":{"x":{"field":"group","type":"nominal"},"y":{"field":"value","type":"quantitative"}}}'
></molplot-chart>
```

## Events

The component dispatches `molplot:ready` after the initial Vega render:

```javascript
document.querySelector("molplot-chart").addEventListener("molplot:ready", () => {
  console.log("MolPlot ready")
})
```
