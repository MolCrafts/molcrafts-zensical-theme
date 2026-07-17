---
title: MolVis Web Component
description: Embed interactive molecular structures with the MolVis Web Component.
---

# MolVis Web Component

`<molvis-viewer>` embeds an interactive molecular structure in any documentation
page. It supports inline molecular text as well as remote structure files.

## Live example

<figure class="molcrafts-web-component-card">
  <figcaption>
    <span class="molcrafts-web-component-card__package">MolVis</span>
    <strong>Inline water molecule</strong>
    <small>Drag to rotate, scroll to zoom, and use the View control to change representation.</small>
  </figcaption>
  <div class="molcrafts-web-component-preview">
    <molvis-viewer format="xyz" representation="ball-and-stick" controls="view">
      <template data-molvis-source>
3
name=water Connct="[0,1,0,2]"
O  0.0000  0.0000  0.0000
H  0.9572  0.0000  0.0000
H -0.2390  0.9266  0.0000
      </template>
    </molvis-viewer>
  </div>
</figure>

## Enable the component

Load the ESM bundle once in `zensical.toml`:

```toml
extra_javascript = [
  { path = "https://cdn.jsdelivr.net/npm/@molcrafts/molvis-core@latest/dist/elements.js", type = "module" },
]
```

## Parameters

| Attribute | Values | Default | Description |
|---|---|---|---|
| `src` | URL | — | Remote PDB, XYZ, or another supported structure file. |
| `format` | `xyz`, `pdb`, … | inferred from `src` | Required for inline data or URLs without a recognizable extension. |
| `representation` | `ball-and-stick`, `spacefill`, `stick` | `ball-and-stick` | Initial molecular representation. |
| `controls` | Space-separated `view`, `trajectory`, `mode`, `info`, `performance`, `context-menu` | `view trajectory` | Visible viewer controls. |
| `modes` | Space-separated `view`, `select`, `edit`, `manipulate`, `measure` | `view` | Modes the document embed permits. Must include `view`. |
| `mode` | One enabled mode | `view` | Initial interaction mode. |
| `background` | CSS color | viewer default | Canvas background color. |
| `width` | CSS length | `100%` | Viewer width. |
| `height` | CSS length | `420px` | Viewer height. Theme CSS can override it responsively. |

Use either `src` or an inline template, never both.

## Inline structure

Put multiline structure text in a hidden `template` and specify its format:

```html
<molvis-viewer format="xyz" representation="ball-and-stick">
  <template data-molvis-source>
3
name=water Connct="[0,1,0,2]"
O  0.0000  0.0000  0.0000
H  0.9572  0.0000  0.0000
H -0.2390  0.9266  0.0000
  </template>
</molvis-viewer>
```

## Remote structure

```html
<molvis-viewer
  src="https://files.rcsb.org/download/1TQN.pdb"
  representation="spacefill"
  controls="view info context-menu"
></molvis-viewer>
```

The remote server must allow cross-origin browser requests.

## JavaScript API

The element exposes `app` after it is ready and supports `reload()`. Listen for
`molvis:ready` and `molvis:error` to integrate it with surrounding UI:

```javascript
const viewer = document.querySelector("molvis-viewer")

viewer.addEventListener("molvis:ready", ({ detail }) => {
  console.log("MolVis ready", detail.app)
})

viewer.addEventListener("molvis:error", ({ detail }) => {
  console.error(detail.error)
})
```
