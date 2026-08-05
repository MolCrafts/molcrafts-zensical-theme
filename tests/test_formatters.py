from __future__ import annotations

from pathlib import Path

import pytest

from molcrafts_zensical_theme.formatters import (
    _stage_local_molplot_bundle,
    _stage_local_molvis_bundle,
    _stage_local_molvis_sketch_bundle,
    _stage_local_molvis_stage_bundle,
    molplot_fence,
    molplot_validator,
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


def test_molvis_fence_strips_leading_trailing_blank_lines() -> None:
    """Pretty-printed fence bodies must not leave blank XYZ frame headers."""
    html = molvis_fence(
        "\n\n2\nH2\nH 0 0 0\nH 0 0 1\n\n",
        "molvis",
        "molvis",
        {},
        None,
        attrs={"format": "xyz"},
    )
    start = html.index("<template data-molvis-source>") + len(
        "<template data-molvis-source>"
    )
    end = html.index("</template>")
    body = html[start:end]
    assert body.startswith("2\n")
    assert body.endswith("H 0 0 1")
    assert not body.startswith("\n")
    assert not body.endswith("\n")


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


def test_molvis_stage_bundle_is_staged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stage only from npm package path (or MOLVIS_STAGE_DIR)."""
    bundle = (
        tmp_path / "node_modules" / "@molcrafts" / "molvis-stage" / "dist"
    )
    bundle.mkdir(parents=True)
    (bundle / "viewer.js").write_text("export {};", encoding="utf-8")
    (bundle / "runtime.js").write_text("export {};", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    _stage_local_molvis_stage_bundle()

    staged = tmp_path / "docs" / "assets" / "molvis-stage"
    assert (staged / "viewer.js").read_text(encoding="utf-8") == "export {};"
    assert (staged / "runtime.js").is_file()


def test_molvis_sketch_bundle_is_staged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = (
        tmp_path / "node_modules" / "@molcrafts" / "molvis-sketch" / "dist"
    )
    bundle.mkdir(parents=True)
    (bundle / "index.js").write_text("export {};", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    _stage_local_molvis_sketch_bundle()

    staged = tmp_path / "docs" / "assets" / "molvis-sketch"
    assert (staged / "index.js").read_text(encoding="utf-8") == "export {};"


def test_molvis_bundle_stages_stage_and_sketch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stage = tmp_path / "node_modules" / "@molcrafts" / "molvis-stage" / "dist"
    sketch = tmp_path / "node_modules" / "@molcrafts" / "molvis-sketch" / "dist"
    stage.mkdir(parents=True)
    sketch.mkdir(parents=True)
    (stage / "viewer.js").write_text("stage", encoding="utf-8")
    (sketch / "index.js").write_text("sketch", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    _stage_local_molvis_bundle()

    assert (
        tmp_path / "docs" / "assets" / "molvis-stage" / "viewer.js"
    ).read_text(encoding="utf-8") == "stage"
    assert (
        tmp_path / "docs" / "assets" / "molvis-sketch" / "index.js"
    ).read_text(encoding="utf-8") == "sketch"


def test_legacy_core_dist_and_old_package_name_are_not_used(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Monorepo-relative core/dist and old molvis-core package must not stage."""
    legacy_core = tmp_path / "core" / "dist"
    legacy_core.mkdir(parents=True)
    (legacy_core / "viewer.js").write_text("export {};", encoding="utf-8")

    old_pkg = tmp_path / "node_modules" / "@molcrafts" / "molvis-core" / "dist"
    old_pkg.mkdir(parents=True)
    (old_pkg / "elements.js").write_text("export {};", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    _stage_local_molvis_bundle()

    assert not (tmp_path / "docs" / "assets" / "molvis-core").exists()
    assert not (tmp_path / "docs" / "assets" / "molvis-stage").exists()
    assert not (tmp_path / "docs" / "assets" / "molvis-sketch").exists()


def test_molplot_fence_embeds_vega_lite_json() -> None:
    html = molplot_fence(
        "mark: point\ndata:\n  values:\n    - {x: 1, y: 2}\n"
        "encoding:\n  x: {field: x, type: quantitative}\n"
        "  y: {field: y, type: quantitative}\n",
        "molplot",
        "molplot",
        {"preset": "molplot", "theme": "auto"},
        None,
    )
    assert "<molplot-chart" in html
    assert 'preset="molplot"' in html
    assert 'theme="auto"' in html
    assert 'aspect="16:10"' in html
    assert '"x": 1' in html
    assert "application/json" in html
    # Docs config supplies font family; sizes come from the host chart.
    assert "Times New Roman" in html


def test_molplot_fence_resolves_dollar_file_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    docs = tmp_path / "docs"
    data = docs / "data"
    data.mkdir(parents=True)
    (data / "pts.json").write_text(
        '[{"x": 1, "y": 2}, {"x": 3, "y": 4}]\n', encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    html = molplot_fence(
        "mark: point\n"
        "data: {$file: data/pts.json}\n"
        "encoding:\n"
        "  x: {field: x, type: quantitative}\n"
        "  y: {field: y, type: quantitative}\n",
        "molplot",
        "molplot",
        {"preset": "molplot"},
        None,
    )
    assert "molplot-error" not in html
    assert '"values"' in html
    assert '"x": 1' in html
    assert '"y": 4' in html
    assert "$file" not in html


def test_molplot_fence_dollar_file_as_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    docs = tmp_path / "docs"
    data = docs / "data"
    data.mkdir(parents=True)
    (data / "pts.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    html = molplot_fence(
        "mark: point\n"
        "data: {$file: data/pts.csv, $as: url}\n"
        "encoding:\n"
        "  x: {field: x, type: quantitative}\n"
        "  y: {field: y, type: quantitative}\n",
        "molplot",
        "molplot",
        {},
        None,
    )
    assert "molplot-error" not in html
    assert '"url": "data/pts.csv"' in html
    assert '"type": "csv"' in html


def test_molplot_fence_missing_file_is_inline_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "docs").mkdir()
    monkeypatch.chdir(tmp_path)
    html = molplot_fence(
        "data: {$file: missing.json}\nmark: point\n",
        "molplot",
        "molplot",
        {},
        None,
    )
    assert "molplot-error" in html
    assert "not found" in html


def test_molplot_fence_respects_explicit_aspect() -> None:
    html = molplot_fence(
        "mark: point\ndata:\n  values:\n    - {x: 1, y: 2}\n"
        "encoding:\n  x: {field: x, type: quantitative}\n"
        "  y: {field: y, type: quantitative}\n",
        "molplot",
        "molplot",
        {"preset": "molplot", "aspect": "4:3"},
        None,
    )
    assert 'aspect="4:3"' in html
    assert 'aspect="16:10"' not in html


def test_molplot_validator_rejects_unknown_options() -> None:
    options: dict = {}
    assert molplot_validator(
        "molplot",
        {"preset": "molplot"},
        options,
        {},
        None,
    )
    assert options["preset"] == "molplot"
    assert not molplot_validator(
        "molplot",
        {"bogus": "1"},
        {},
        {},
        None,
    )


def test_molplot_npm_package_bundle_is_staged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = tmp_path / "node_modules" / "@molcrafts" / "molplot" / "dist"
    bundle.mkdir(parents=True)
    (bundle / "elements.js").write_text("export {};", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    _stage_local_molplot_bundle()

    staged = tmp_path / "docs" / "assets" / "molplot"
    assert (staged / "elements.js").read_text(encoding="utf-8") == "export {};"
