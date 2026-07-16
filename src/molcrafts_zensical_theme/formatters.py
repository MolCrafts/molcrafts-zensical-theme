"""Formatter-backed MolVis components for MolCrafts documentation sites."""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
import shutil
from typing import Any, Mapping

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


def _stage_local_molvis_bundle() -> None:
    """Copy a local MolVis elements build into the documentation assets.

    This keeps ``zensical serve`` faithful to a MolVis source checkout instead
    of silently loading an older npm release. Published documentation builds
    can set ``MOLVIS_ELEMENTS_DIR`` explicitly; when no local build exists the
    small browser loader falls back to the npm CDN.
    """
    cwd = Path.cwd()
    configured = os.environ.get("MOLVIS_ELEMENTS_DIR")
    candidates = [
        Path(configured).expanduser() if configured else None,
        cwd / "core" / "dist",
        cwd / "node_modules" / "@molcrafts" / "molvis-core" / "dist",
    ]
    source = next(
        (
            candidate.resolve()
            for candidate in candidates
            if candidate is not None
            and (candidate / "elements.js").is_file()
        ),
        None,
    )
    if source is None:
        return

    assets_dir = Path(
        os.environ.get("MOLVIS_DOCS_ASSET_DIR", cwd / "docs" / "assets")
    )
    target = assets_dir / "molvis-core"
    if source == target.resolve():
        return
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        dirs_exist_ok=True,
        copy_function=_copy_if_changed,
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
    content = escape(source, quote=False)
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
    if source.strip():
        content = (
            "<template data-molvis-source>"
            f"{escape(source, quote=False)}"
            "</template>"
        )
    return (
        f"<molvis-style-gallery {attributes}>"
        f"{content}</molvis-style-gallery>"
    )


# Zensical imports formatter callables while resolving its configuration. Stage
# the bundle here so it is present before the static-asset scan starts. The
# formatter calls above keep it fresh during a long-running development server.
_stage_local_molvis_bundle()


__all__ = ["molvis_fence", "molvis_gallery_fence"]
