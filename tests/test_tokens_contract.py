"""Shared brand tokens must stay complete and bit-identical to index when co-located."""

from __future__ import annotations

import re
from pathlib import Path

THEME_TOKENS = (
    Path(__file__).resolve().parents[1]
    / "src/molcrafts_zensical_theme/templates/assets/stylesheets/tokens.css"
)

# Sibling checkout under the monorepo workspace (optional).
INDEX_TOKENS = (
    Path(__file__).resolve().parents[2] / "molcrafts-index/src/styles/brand-tokens.css"
)

REQUIRED_HEX = {
    "--molcrafts-forest": "#18432b",
    "--molcrafts-forest-light": "#2a6744",
    "--molcrafts-forest-dark": "#0e2b1b",
    "--molcrafts-cream": "#fbf6e4",
    "--molcrafts-cream-soft": "#fffaf0",
    "--molcrafts-sand": "#f2da9d",
    "--molcrafts-sand-strong": "#c8841d",
    "--molcrafts-ink": "#14271d",
    "--molcrafts-slate": "#101811",
    "--molcrafts-radius": "0.4rem",
}

PROP_RE = re.compile(
    r"(--molcrafts-[\w-]+)\s*:\s*([^;]+);",
    re.MULTILINE,
)


def _props(css: str) -> dict[str, str]:
    return {name: value.strip() for name, value in PROP_RE.findall(css)}


def test_tokens_file_exists() -> None:
    assert THEME_TOKENS.is_file(), f"missing {THEME_TOKENS}"


def test_required_brand_anchors() -> None:
    props = _props(THEME_TOKENS.read_text(encoding="utf-8"))
    for name, expected in REQUIRED_HEX.items():
        assert name in props, f"missing {name}"
        assert props[name].lower() == expected.lower(), (
            f"{name}: got {props[name]!r}, expected {expected!r}"
        )


def test_hsl_channels_present_for_index() -> None:
    props = _props(THEME_TOKENS.read_text(encoding="utf-8"))
    for name in (
        "--molcrafts-forest-hsl",
        "--molcrafts-forest-light-hsl",
        "--molcrafts-cream-hsl",
        "--molcrafts-slate-hsl",
    ):
        assert name in props, f"missing HSL channel {name}"
        # "H S% L%" — three space-separated components
        parts = props[name].split()
        assert len(parts) == 3, f"{name} should be 'H S% L%', got {props[name]!r}"


def test_identical_to_index_when_checkout_present() -> None:
    """Manual sync: if both repos sit under molcrafts/, files must match exactly."""
    if not INDEX_TOKENS.is_file():
        return
    theme = THEME_TOKENS.read_text(encoding="utf-8")
    index = INDEX_TOKENS.read_text(encoding="utf-8")
    assert theme == index, (
        "brand tokens drifted.\n"
        f"  theme: {THEME_TOKENS}\n"
        f"  index: {INDEX_TOKENS}\n"
        "Copy one file over the other (they must be identical)."
    )
