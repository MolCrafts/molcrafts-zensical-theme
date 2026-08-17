from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path


def _theme_dir() -> Path:
    """Resolve the theme directory the way Zensical's `get_theme_dir` does."""
    theme = next(
        ep for ep in entry_points(group="mkdocs.themes") if ep.name == "molcrafts"
    )
    return Path(str(theme.load().__file__)).parent


def test_theme_directory_ships_the_theme_files() -> None:
    theme_dir = _theme_dir()

    assert (theme_dir / "mkdocs_theme.yml").is_file()
    assert (theme_dir / "main.html").is_file()
    assert (theme_dir / "partials" / "copyright.html").is_file()
    assert (theme_dir / "assets" / "stylesheets" / "molcrafts.css").is_file()


def test_embeds_guard_reports_unregistered_molplot_in_console() -> None:
    """A 404'd elements.js must not stay silent — guard names the tag and hint."""
    root = Path(__file__).resolve().parents[1]
    templates = root / "src" / "molcrafts_zensical_theme" / "templates"
    guard = (templates / "assets" / "javascripts" / "embeds-guard.js").read_text(
        encoding="utf-8"
    )
    main = (templates / "main.html").read_text(encoding="utf-8")
    assert "customElements.get('molplot-chart')" in guard
    assert "console.error" in guard
    assert "assets/molplot/elements.js" in guard
    assert "enable_molplot" in guard
    assert "whenDefined" in guard
    assert "embeds-guard.js" in main


def test_theme_injects_molplot_from_enable_flag() -> None:
    """Products only flip extra.molcrafts.enable_molplot; theme owns the URLs."""
    root = Path(__file__).resolve().parents[1]
    main = (
        root / "src" / "molcrafts_zensical_theme" / "templates" / "main.html"
    ).read_text(encoding="utf-8")
    assert "enable_molplot" in main
    assert "assets/molplot/elements.js" in main
    assert "cdn.jsdelivr.net/npm/@molcrafts/molplot" in main


def test_theme_directory_ships_no_package_code() -> None:
    """Zensical copies every non-template file from the theme directory into the
    built site, so package modules must live outside it — only the `__init__.py`
    that makes the directory importable may stay."""
    modules = sorted(path.name for path in _theme_dir().glob("*.py"))

    assert modules == ["__init__.py"]


def test_formatters_live_outside_the_theme_directory() -> None:
    from molcrafts_zensical_theme import formatters

    assert Path(str(formatters.__file__)).parent != _theme_dir()
