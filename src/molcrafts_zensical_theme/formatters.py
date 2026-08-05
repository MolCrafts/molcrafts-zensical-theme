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
# Fence body = Vega-Lite top-level spec (YAML/JSON).
# Data refs (resolved at build time, relative to docs root):
#   data: {$file: data/foo.json}          → {values: [...]}
#   data: {$file: data/foo.csv, $as: url} → {url: "data/foo.csv"} (site path)
#   data: {$url: https://…}               → {url: "https://…"}
# Named datasets: datasets: {curve: {$file: data/curve.json}}

MOLPLOT_OPTIONS = ("preset", "theme", "type", "width", "aspect", "root")


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


# ── MolPlot fence ──────────────────────────────────────────────────────────
# Contract: fence body is a Vega-Lite top-level spec (YAML or JSON).
# Formatter: parse → resolve $file/$url data refs → docs config defaults → embed.


def _load_molplot_spec(source: str) -> Any:
    """Parse fence body (YAML preferred, JSON fallback) into a Python object."""
    text = source.strip()
    if not text:
        raise ValueError("empty molplot fence body")
    try:
        import yaml
    except ImportError:  # pragma: no cover
        return json.loads(text)
    return yaml.safe_load(text)


_SERIF_STACK = (
    "Times New Roman, Times, STIX Two Text, STIXGeneral, "
    "Latin Modern Roman, serif"
)
# Docs defaults only (font family). Sizes come from molplot host fontScale.
_MOLPLOT_DOCS_CONFIG: dict[str, Any] = {
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
    "legend": {"labelFont": _SERIF_STACK, "titleFont": _SERIF_STACK},
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


def _apply_docs_config(spec: Any) -> Any:
    """Merge docs font defaults under author ``config`` (author wins)."""
    if not isinstance(spec, dict):
        return spec
    existing = spec.get("config")
    if isinstance(existing, dict):
        spec["config"] = _deep_merge_dict(_MOLPLOT_DOCS_CONFIG, existing)
    else:
        spec["config"] = dict(_MOLPLOT_DOCS_CONFIG)
    return spec


def _docs_dir(md: Any = None, options: Mapping[str, Any] | None = None) -> Path:
    """Resolve the documentation root for ``$file`` paths."""
    if options and options.get("root"):
        return Path(str(options["root"])).expanduser().resolve()
    for key in ("DOCS_DIR", "MOLPLOT_DOCS_DIR"):
        env = os.environ.get(key)
        if env:
            return Path(env).expanduser().resolve()
    # zensical / mkdocs usually run with project cwd; docs/ is conventional.
    cwd = Path.cwd()
    if (cwd / "docs").is_dir():
        return (cwd / "docs").resolve()
    return cwd.resolve()


def _load_data_file(path: Path) -> Any:
    """Load JSON / YAML / CSV from *path*."""
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        import yaml

        return yaml.safe_load(text)
    if suffix == ".csv":
        import csv
        from io import StringIO

        rows = list(csv.DictReader(StringIO(text)))
        # Coerce plain numeric strings when possible.
        for row in rows:
            for k, v in list(row.items()):
                if v is None or v == "":
                    continue
                try:
                    row[k] = int(v)
                except ValueError:
                    try:
                        row[k] = float(v)
                    except ValueError:
                        pass
        return rows
    raise ValueError(
        f"unsupported molplot data file type '{suffix}' ({path.name}); "
        "use .json, .yaml, .yml, or .csv"
    )


def _file_ref_to_vl_data(
    path: Path,
    *,
    docs_dir: Path,
    as_mode: str,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    """Turn a resolved path into a Vega-Lite ``data`` object."""
    if as_mode == "url":
        try:
            rel = path.resolve().relative_to(docs_dir.resolve())
        except ValueError as exc:
            raise ValueError(
                f"$file path escapes docs root: {path}"
            ) from exc
        # Site URL from docs root (zensical serves docs/ as site root content).
        url = str(rel).replace("\\", "/")
        out: dict[str, Any] = {"url": url}
        if path.suffix.lower() == ".csv" and "format" not in extra:
            out["format"] = {"type": "csv"}
        out.update(extra)
        return out

    # Default: embed as values so the chart works offline / without path hacks.
    raw = _load_data_file(path)
    if isinstance(raw, list):
        out = {"values": raw}
    elif isinstance(raw, dict):
        if any(k in raw for k in ("values", "url", "name", "sequence")):
            out = dict(raw)
        else:
            out = {"values": [raw]}
    else:
        raise ValueError(f"cannot use data from {path.name}: expected list or object")
    out.update(extra)
    return out


def _resolve_data_refs(node: Any, docs_dir: Path) -> Any:
    """Walk the VL tree; expand ``{$file: …}`` / ``{$url: …}`` data refs."""
    if isinstance(node, list):
        return [_resolve_data_refs(item, docs_dir) for item in node]
    if not isinstance(node, dict):
        return node

    if "$file" in node or "$url" in node:
        extra = {
            k: _resolve_data_refs(v, docs_dir)
            for k, v in node.items()
            if not str(k).startswith("$")
        }
        if "$url" in node:
            out = {"url": str(node["$url"])}
            out.update(extra)
            return out
        rel = str(node["$file"])
        docs_root = docs_dir.resolve()
        path = (docs_root / rel).resolve()
        try:
            path.relative_to(docs_root)
        except ValueError as exc:
            raise ValueError(
                f"$file path escapes docs root ({docs_dir}): {rel}"
            ) from exc
        if not path.is_file():
            raise ValueError(f"molplot $file not found: {rel} (docs={docs_dir})")
        as_mode = str(node.get("$as", "values")).lower()
        if as_mode not in {"values", "url"}:
            raise ValueError(f"unknown $as mode: {as_mode} (use values|url)")
        return _file_ref_to_vl_data(
            path, docs_dir=docs_root, as_mode=as_mode, extra=extra
        )

    return {k: _resolve_data_refs(v, docs_dir) for k, v in node.items()}


def render_molplot_element(
    source: str,
    *,
    preset: str | None = None,
    theme: str | None = None,
    width: str | None = None,
    aspect: str | None = None,
    docs_dir: Path | None = None,
) -> str:
    """YAML/JSON Vega-Lite → ``<molplot-chart>`` (parse, resolve data, embed)."""
    try:
        spec = _load_molplot_spec(source)
        if not isinstance(spec, dict):
            raise ValueError("fence body must be a mapping (Vega-Lite top-level)")
        root = docs_dir if docs_dir is not None else _docs_dir()
        spec = _resolve_data_refs(spec, root)
        spec = _apply_docs_config(spec)
    except Exception as exc:  # noqa: BLE001 - report parse/data errors inline
        message = escape(f"molplot: {exc}")
        return f'<div class="molplot-error">{message}</div>'

    resolved_aspect = (aspect or "16:10").strip() or "16:10"
    attrs = ""
    if preset:
        attrs += f' preset="{escape(preset, quote=True)}"'
    if theme:
        attrs += f' theme="{escape(theme, quote=True)}"'
    if width:
        attrs += f' width="{escape(width, quote=True)}"'
    attrs += f' aspect="{escape(resolved_aspect, quote=True)}"'

    payload = json.dumps(spec, ensure_ascii=False)
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
    """Accept known molplot fence-header options."""
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
    """Parse fence YAML as Vega-Lite, resolve ``$file`` data, emit chart."""
    del language, css_class, kwargs
    _stage_local_molplot_bundle()
    return render_molplot_element(
        source,
        preset=options.get("preset"),
        theme=options.get("theme"),
        width=options.get("width"),
        aspect=options.get("aspect"),
        docs_dir=_docs_dir(md, options),
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
