from __future__ import annotations

from pathlib import Path

import pytest

from molcrafts_zensical_theme.formatters import (
    _stage_local_molvis_bundle,
    molvis_fence,
    molvis_gallery_fence,
)


def test_molvis_fence_escapes_inline_source() -> None:
    html = molvis_fence(
        "2\nwater & ions\nH 0 0 0\nH <1 0 0",
        "molvis",
        "molvis",
        {},
        None,
        attrs={"format": "xyz"},
    )
    assert '<molvis-viewer format="xyz" class="molvis">' in html
    assert "water &amp; ions" in html
    assert "H &lt;1 0 0" in html


def test_gallery_fence_supports_remote_source() -> None:
    html = molvis_gallery_fence(
        "",
        "molvis-gallery",
        "molvis-gallery",
        {},
        None,
        attrs={"src": "../assets/aspirin.sdf", "format": "sdf"},
    )
    assert '<molvis-style-gallery src="../assets/aspirin.sdf"' in html
    assert "<template" not in html


def test_gallery_fence_rejects_unknown_representation() -> None:
    with pytest.raises(ValueError, match="Unknown molvis representation"):
        molvis_gallery_fence(
            "2\nH2\nH 0 0 0\nH 0 0 1",
            "molvis-gallery",
            "molvis-gallery",
            {},
            None,
            attrs={"format": "xyz", "representations": "flat bogus"},
        )


def test_local_bundle_is_staged_as_a_documentation_asset(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = tmp_path / "core" / "dist"
    bundle.mkdir(parents=True)
    (bundle / "elements.js").write_text("export {};", encoding="utf-8")
    (bundle / "runtime.js").write_text("export {};", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    _stage_local_molvis_bundle()

    staged = tmp_path / "docs" / "assets" / "molvis-core"
    assert (staged / "elements.js").read_text(encoding="utf-8") == "export {};"
    assert (staged / "runtime.js").is_file()
