"""Product sites must not re-own the visual system — theme owns surface CSS."""

from __future__ import annotations

import re
from pathlib import Path

THEME_CSS = (
    Path(__file__).resolve().parents[1]
    / "src/molcrafts_zensical_theme/templates/assets/stylesheets/molcrafts.css"
)

README = Path(__file__).resolve().parents[1] / "README.md"

# Surface components every product docs home may use. Re-skinning these in a
# product extra.css fights the theme (see README iron law).
OWNED_PREFIXES = (
    "molcrafts-home-hero",
    "molcrafts-manual-home",
    "molcrafts-manual-section",
    "molcrafts-workflow-list",
    "molcrafts-feature-matrix",
    "molcrafts-doc-map",
    "molcrafts-tile-grid",
    "molcrafts-link-list",
    "molcrafts-manual-grid",
    "molcrafts-manual-list",
    "molcrafts-manual-index",
    "molcrafts-figure",
)


def test_theme_ships_owned_surface_selectors() -> None:
    css = THEME_CSS.read_text(encoding="utf-8")
    for prefix in OWNED_PREFIXES:
        assert f".{prefix}" in css, f"theme missing owned surface .{prefix}"


def test_readme_documents_product_extra_css_iron_law() -> None:
    text = README.read_text(encoding="utf-8")
    assert "Product `extra.css` — iron law" in text
    assert "must not re-skin the theme" in text.lower() or "must not re-skin" in text


def test_theme_documents_consumer_rule_in_css() -> None:
    css = THEME_CSS.read_text(encoding="utf-8")
    assert "Product docs set accent in zensical.toml" in css
    assert "product-unique markup" in css


def test_owned_modifiers_exist() -> None:
    """Shared layout modifiers live in the theme, not product extra.css."""
    css = THEME_CSS.read_text(encoding="utf-8")
    for name in (
        "molcrafts-feature-matrix--cards",
        "molcrafts-feature-matrix__icon",
        "molcrafts-doc-map--cards",
        "molcrafts-manual-section--flip",
        "molcrafts-manual-section--body-col",
        "molcrafts-tile-grid",
        "molcrafts-link-list",
    ):
        assert name in css, f"missing theme modifier/component {name}"


def test_no_docs_product_surface_in_theme() -> None:
    """Theme CSS must not ship product-docs skins (those belong in product extra.css).

    Web-component fence namespaces (``.molvis-style-gallery*``,
    ``.molplot-chart*``) are theme-owned runtime helpers, not docs skins.
    """
    css = THEME_CSS.read_text(encoding="utf-8")
    # Product docs that consume this theme for manuals — not fence WC packages.
    banned = re.findall(
        r"\.(molpy|molpack|molrs|molq|molnex|molexp|molcfg|mollog|molrec|molmcp)-[a-zA-Z0-9_-]+",
        css,
    )
    assert banned == [], f"theme CSS must not define product-docs classes: {banned}"
