"""Doc-site fence formatters for MolVis and MolPlot Web Components.

Packages follow the **same contract**:

1. **Build time (Python):** a superfences formatter in *this theme package*
   turns a Markdown fence into a Web Component tag. Consuming sites only need
   ``molcrafts-zensical-theme`` (+ zensical) — not the molvis / molplot
   Python libraries.
2. **Run time (browser):** the corresponding npm CDN / staged bundle upgrades
   the custom element. Sites load it once via ``extra_javascript``.

MolVis is **two** npm packages after the monorepo split:

- ``@molcrafts/molvis-stage`` — 3D (CDN entry ``dist/viewer.js``)
- ``@molcrafts/molvis-sketch`` — 2D (CDN entry ``dist/index.js``)

Optional local staging (monorepo / ``npm link``) uses:

1. ``$ENV_*_DIR`` override
2. ``node_modules/@molcrafts/<package>/dist`` (must contain the entry file)
3. otherwise leave the CDN path alone

Never stage monorepo-relative engine paths (``stage/dist``, ``sketch/dist``).
"""

from __future__ import annotations

from html import escape
import json
import os
from pathlib import Path
import shutil
from typing import Any, Mapping

# ── MolVis vocabulary ──────────────────────────────────────────────────────

FORMATS = {
    "pdb",
    "xyz",
    "cif",
    "lammps",
    "lammps-dump",
    "sdf",
    "dcd",
    "cube",
    "chgcar",
    "gro",
    "mol2",
    "poscar",
    "trr",
    "xtc",
}
CONTROLS = {
    "view",
    "trajectory",
    "mode",
    "info",
    "performance",
    "context-menu",
}
MODES = {"view", "select", "edit", "manipulate", "measure"}
REPRESENTATIONS = {
    "ball-and-stick",
    "flat",
    "ball-and-tube",
    "tube",
    "metal-tube",
    "wireframe",
    "bubble",
    "spacefill",
    "skeletal",
    "graph",
}
VIEWER_ATTRIBUTES = {
    "format",
    "controls",
    "modes",
    "mode",
    "representation",
    "background",
    "width",
    "height",
}
GALLERY_ATTRIBUTES = {
    "src",
    "format",
    "representations",
    "background",
    "rotation-speed",
}

# ── MolPlot vocabulary ─────────────────────────────────────────────────────

MOLPLOT_OPTIONS = ("preset", "theme", "type", "width", "aspect")


def _tokens(value: str) -> set[str]:
    return {item for item in value.split() if item}


def _copy_if_changed(source: str, target: str) -> str:
    """Copy one bundle file only when its contents may have changed."""
    source_path = Path(source)
    target_path = Path(target)
    if target_path.is_file():
        source_stat = source_path.stat()
        target_stat = target_path.stat()
        if (
            source_stat.st_size == target_stat.st_size
            and source_stat.st_mtime_ns == target_stat.st_mtime_ns
        ):
            return str(target_path)
    return shutil.copy2(source_path, target_path)


def _stage_npm_bundle(
    *,
    env_var: str,
    npm_package: str,
    asset_subdir: str,
    entry_file: str,
) -> None:
    """Stage ``@molcrafts/<npm_package>/dist`` under ``docs/assets/<asset_subdir>``.

    ``entry_file`` is the marker that must exist in ``dist`` (e.g. ``viewer.js``,
    ``index.js``, ``elements.js``) so incomplete installs are skipped.
    """
    cwd = Path.cwd()
    configured = os.environ.get(env_var)
    candidates = [
        Path(configured).expanduser() if configured else None,
        cwd / "node_modules" / "@molcrafts" / npm_package / "dist",
    ]
    source = next(
        (
            candidate.resolve()
            for candidate in candidates
            if candidate is not None and (candidate / entry_file).is_file()
        ),
        None,
    )
    if source is None:
        return

    assets_dir = Path(
        os.environ.get("MOLCRAFTS_DOCS_ASSET_DIR", cwd / "docs" / "assets")
    )
    target = assets_dir / asset_subdir
    if source == target.resolve():
        return
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        dirs_exist_ok=True,
        copy_function=_copy_if_changed,
    )


def _stage_local_molvis_stage_bundle() -> None:
    """Stage ``@molcrafts/molvis-stage`` into ``docs/assets/molvis-stage``."""
    _stage_npm_bundle(
        env_var="MOLVIS_STAGE_DIR",
        npm_package="molvis-stage",
        asset_subdir="molvis-stage",
        entry_file="viewer.js",
    )


def _stage_local_molvis_sketch_bundle() -> None:
    """Stage ``@molcrafts/molvis-sketch`` into ``docs/assets/molvis-sketch``."""
    _stage_npm_bundle(
        env_var="MOLVIS_SKETCH_DIR",
        npm_package="molvis-sketch",
        asset_subdir="molvis-sketch",
        entry_file="index.js",
    )


def _stage_local_molvis_bundle() -> None:
    """Stage both MolVis product packages (3D stage + 2D sketch)."""
    _stage_local_molvis_stage_bundle()
    _stage_local_molvis_sketch_bundle()


def _stage_local_molplot_bundle() -> None:
    """Stage ``@molcrafts/molplot`` into ``docs/assets/molplot``."""
    _stage_npm_bundle(
        env_var="MOLPLOT_ELEMENTS_DIR",
        npm_package="molplot",
        asset_subdir="molplot",
        entry_file="elements.js",
    )


def _attrs(kwargs: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in kwargs.get("attrs", {}).items()
    }


def _rendered_attributes(
    attrs: Mapping[str, str],
    css_class: str,
    kwargs: Mapping[str, Any],
) -> str:
    rendered = [
        f'{key}="{escape(value, quote=True)}"'
        for key, value in attrs.items()
    ]
    classes = [css_class, *kwargs.get("classes", [])]
    classes = [value for value in classes if value]
    if classes:
        rendered.append(
            f'class="{escape(" ".join(classes), quote=True)}"'
        )
    if id_value := kwargs.get("id_value"):
        rendered.append(f'id="{escape(str(id_value), quote=True)}"')
    return " ".join(rendered)


def _validate_viewer(attrs: Mapping[str, str]) -> None:
    unknown = set(attrs) - VIEWER_ATTRIBUTES
    if unknown:
        raise ValueError(
            "Unknown molvis fence attribute(s): "
            + ", ".join(sorted(unknown))
        )

    format_name = attrs.get("format", "").strip()
    if not format_name:
        raise ValueError(
            'A molvis fence requires format="pdb", format="xyz", etc.'
        )
    if format_name not in FORMATS:
        raise ValueError(f"Unsupported molvis format: {format_name}")

    controls = _tokens(attrs.get("controls", "view trajectory"))
    if invalid := controls - CONTROLS:
        raise ValueError(
            f"Unknown molvis control(s): {', '.join(sorted(invalid))}"
        )

    modes = _tokens(attrs.get("modes", "view"))
    if invalid := modes - MODES:
        raise ValueError(
            f"Unknown molvis mode(s): {', '.join(sorted(invalid))}"
        )
    if "view" not in modes:
        raise ValueError('molvis fence modes must include "view"')

    mode = attrs.get("mode", "view")
    if mode not in modes:
        raise ValueError(
            f'Initial molvis mode "{mode}" is not included in modes'
        )

    representation = attrs.get("representation", "ball-and-stick")
    if representation not in REPRESENTATIONS:
        raise ValueError(f"Unknown molvis representation: {representation}")


def _validate_gallery(source: str, attrs: Mapping[str, str]) -> None:
    unknown = set(attrs) - GALLERY_ATTRIBUTES
    if unknown:
        raise ValueError(
            "Unknown molvis-gallery fence attribute(s): "
            + ", ".join(sorted(unknown))
        )

    src = attrs.get("src", "").strip()
    has_inline_source = bool(source.strip())
    if src and has_inline_source:
        raise ValueError(
            "A molvis-gallery fence accepts either src or inline source, "
            "not both"
        )
    if not src and not has_inline_source:
        raise ValueError(
            "A molvis-gallery fence requires src or inline molecular source"
        )

    format_name = attrs.get("format", "").strip()
    if has_inline_source and not format_name:
        raise ValueError("An inline molvis-gallery fence requires format")
    if format_name and format_name not in FORMATS:
        raise ValueError(f"Unsupported molvis format: {format_name}")

    if invalid := (
        _tokens(attrs.get("representations", "")) - REPRESENTATIONS
    ):
        raise ValueError(
            "Unknown molvis representation(s): "
            + ", ".join(sorted(invalid))
        )

    rotation_speed = attrs.get("rotation-speed", "0.08")
    try:
        speed = float(rotation_speed)
    except ValueError as error:
        raise ValueError(
            "molvis-gallery rotation-speed must be a number"
        ) from error
    if speed < 0:
        raise ValueError(
            "molvis-gallery rotation-speed must be non-negative"
        )


def _normalize_molvis_source(source: str) -> str:
    """Strip BOM and outer blank lines so XYZ ``len()`` never sees a blank header.

    molrs ≤0.8.2 treats a leading/trailing blank line as a new frame's atom
    count and throws ``XYZ len error: invalid atom count:``. Fence bodies and
    pretty-printed HTML templates often pick those up from indentation.
    """
    text = source.lstrip("\ufeff")
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def molvis_fence(
    source: str,
    language: str,
    css_class: str,
    options: Mapping[str, str],
    md: Any,
    **kwargs: Any,
) -> str:
    """Emit a validated ``molvis-viewer`` Web Component."""
    del language, options, md
    _stage_local_molvis_bundle()
    attrs = _attrs(kwargs)
    _validate_viewer(attrs)
    attributes = _rendered_attributes(attrs, css_class, kwargs)
    content = escape(_normalize_molvis_source(source), quote=False)
    return (
        f"<molvis-viewer {attributes}>"
        f"<template data-molvis-source>{content}</template>"
        "</molvis-viewer>"
    )


def molvis_gallery_fence(
    source: str,
    language: str,
    css_class: str,
    options: Mapping[str, str],
    md: Any,
    **kwargs: Any,
) -> str:
    """Emit a shared-engine ``molvis-style-gallery`` Web Component."""
    del language, options, md
    _stage_local_molvis_bundle()
    attrs = _attrs(kwargs)
    _validate_gallery(source, attrs)
    attributes = _rendered_attributes(attrs, css_class, kwargs)
    content = ""
    normalized = _normalize_molvis_source(source)
    if normalized:
        content = (
            "<template data-molvis-source>"
            f"{escape(normalized, quote=False)}"
            "</template>"
        )
    return (
        f"<molvis-style-gallery {attributes}>"
        f"{content}</molvis-style-gallery>"
    )


# ── MolPlot fence (same ownership model as MolVis) ─────────────────────────


def _load_molplot_spec(source: str) -> Any:
    """Parse a fenced body (YAML or JSON) into a Vega-Lite spec object."""
    try:
        import yaml
    except ImportError:  # pragma: no cover - JSON-only fallback
        return json.loads(source)
    return yaml.safe_load(source)


# Screen / docs type scale. Paper preset is ~9–12 px; docs aim ~1.6–1.8× so
# labels read clearly without crushing the plot (3 legends need room).
_SERIF_STACK = (
    "Times New Roman, Times, STIX Two Text, STIXGeneral, "
    "Latin Modern Roman, serif"
)
# Docs type: Times/math serif only. Font *sizes* come from molplot
# fontScaleForWidth (2× paper at design width, tracks host) — do not freeze
# labelFontSize/titleFontSize here or dynamic 200% scaling is lost.
_MOLPLOT_DOCS_TYPE: dict[str, Any] = {
    "padding": {"left": 14, "right": 14, "top": 12, "bottom": 14},
    "font": _SERIF_STACK,
    "axis": {
        "titleFontStyle": "normal",
        "labelFontStyle": "normal",
        "titleFont": _SERIF_STACK,
        "labelFont": _SERIF_STACK,
        "labelOverlap": True,
        "labelFlush": True,
        "titlePadding": 12,
        "labelPadding": 6,
        "labelLimit": 280,
        "titleLimit": 320,
    },
    "legend": {
        "labelFont": _SERIF_STACK,
        "titleFont": _SERIF_STACK,
    },
    "title": {"font": _SERIF_STACK, "fontStyle": "normal"},
    "text": {"font": _SERIF_STACK, "fontStyle": "normal"},
}


def _deep_merge_dict(base: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in over.items():
        prev = out.get(key)
        if isinstance(value, dict) and isinstance(prev, dict):
            out[key] = _deep_merge_dict(prev, value)
        else:
            out[key] = value
    return out


def _apply_docs_type_scale(spec: Any) -> Any:
    """Merge readable screen type sizes into a Vega-Lite spec's ``config``."""
    if not isinstance(spec, dict):
        return spec
    existing = spec.get("config")
    if isinstance(existing, dict):
        # Author config wins over docs defaults on conflicting keys.
        spec["config"] = _deep_merge_dict(_MOLPLOT_DOCS_TYPE, existing)
    else:
        spec["config"] = dict(_MOLPLOT_DOCS_TYPE)
    return spec


def render_molplot_element(
    source: str,
    *,
    preset: str | None = None,
    theme: str | None = None,
    width: str | None = None,
    aspect: str | None = None,
) -> str:
    """YAML/JSON Vega-Lite fence body → ``<molplot-chart>`` Web Component.

    The fence **is** a Vega-Lite spec. This formatter only parses it, applies
    docs type defaults, and embeds the JSON. No geometry / annotation DSL.
    """
    try:
        spec = _load_molplot_spec(source)
    except Exception as exc:  # noqa: BLE001 - report parse errors inline
        message = escape(f"molplot: invalid Vega-Lite spec — {exc}")
        return f'<div class="molplot-error">{message}</div>'

    spec = _apply_docs_type_scale(spec)

    # Docs default: 16:10 — room for side legends without crushing the plot.
    # Authors may override via fence header (e.g. aspect="4:3").
    resolved_aspect = (aspect or "16:10").strip() or "16:10"

    attrs = ""
    if preset:
        attrs += f' preset="{escape(preset, quote=True)}"'
    if theme:
        attrs += f' theme="{escape(theme, quote=True)}"'
    if width:
        attrs += f' width="{escape(width, quote=True)}"'
    attrs += f' aspect="{escape(resolved_aspect, quote=True)}"'

    payload = json.dumps(spec)
    return (
        f'<div class="molplot">'
        f"<molplot-chart{attrs}>"
        f'<script type="application/json">{payload}</script>'
        f"</molplot-chart>"
        f"</div>"
    )


def molplot_validator(
    language: str,
    inputs: dict[str, str],
    options: dict[str, Any],
    attrs: dict[str, Any],
    md: Any,
) -> bool:
    """Accept only known molplot fence-header options."""
    del language, attrs, md
    for key, value in inputs.items():
        if key not in MOLPLOT_OPTIONS:
            return False
        options[key] = value
    return True


def molplot_fence(
    source: str,
    language: str,
    css_class: str,
    options: Mapping[str, Any],
    md: Any,
    **kwargs: Any,
) -> str:
    """Parse fence YAML as Vega-Lite and emit ``<molplot-chart>``."""
    del language, css_class, md, kwargs
    _stage_local_molplot_bundle()
    return render_molplot_element(
        source,
        preset=options.get("preset"),
        theme=options.get("theme"),
        width=options.get("width"),
        aspect=options.get("aspect"),
    )


# Stage bundles at import time so zensical's static-asset scan sees them.
_stage_local_molvis_bundle()
_stage_local_molplot_bundle()


__all__ = [
    "molvis_fence",
    "molvis_gallery_fence",
    "molplot_fence",
    "molplot_validator",
    "render_molplot_element",
    "_stage_local_molvis_bundle",
    "_stage_local_molvis_stage_bundle",
    "_stage_local_molvis_sketch_bundle",
    "_stage_local_molplot_bundle",
]
