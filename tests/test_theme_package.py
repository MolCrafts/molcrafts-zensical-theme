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


def test_theme_directory_ships_no_package_code() -> None:
    """Zensical copies every non-template file from the theme directory into the
    built site, so package modules must live outside it — only the `__init__.py`
    that makes the directory importable may stay."""
    modules = sorted(path.name for path in _theme_dir().glob("*.py"))

    assert modules == ["__init__.py"]


def test_formatters_live_outside_the_theme_directory() -> None:
    from molcrafts_zensical_theme import formatters

    assert Path(str(formatters.__file__)).parent != _theme_dir()
