"""Configuration for the C++ mkdocstrings handler."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from mkdocs.exceptions import PluginError

MembersOrder = Literal["source", "alphabetical"]


def _as_list(value: Any, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    raise PluginError(f"'{field_name}' must be a string or a list of strings")


def _as_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    raise PluginError(f"'{field_name}' must be a boolean")


def _as_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            pass
    raise PluginError(f"'{field_name}' must be an integer")


@dataclass(slots=True)
class CppOptions:
    """Render options passed to the handler."""

    heading_level: int = 2
    show_root_heading: bool = True
    show_root_full_path: bool = False
    members: list[str] | None = None
    members_order: MembersOrder = "source"
    show_private: bool = False
    show_protected: bool = True
    show_source_location: bool = False
    separate_signature: bool = True
    show_template_parameters: bool = True
    show_enum_values: bool = True

    @classmethod
    def from_data(cls, **data: Any) -> CppOptions:
        """Build options from untyped mkdocstrings data."""
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise PluginError(f"Unknown C++ handler option(s): {', '.join(unknown)}")

        values: dict[str, Any] = {}
        for name, value in data.items():
            if name == "heading_level":
                values[name] = _as_int(value, field_name=name)
            elif name in {
                "show_root_heading",
                "show_root_full_path",
                "show_private",
                "show_protected",
                "show_source_location",
                "separate_signature",
                "show_template_parameters",
                "show_enum_values",
            }:
                values[name] = _as_bool(value, field_name=name)
            elif name == "members":
                values[name] = _as_list(value, field_name=name)
            elif name == "members_order":
                if value not in {"source", "alphabetical"}:
                    raise PluginError("'members_order' must be 'source' or 'alphabetical'")
                values[name] = value
            else:
                values[name] = value

        return cls(**values)


@dataclass(slots=True)
class CppConfig:
    """Global handler configuration."""

    input: list[str] = field(default_factory=list)
    file_patterns: list[str] = field(
        default_factory=lambda: ["*.h", "*.hpp", "*.hh", "*.hxx", "*.cpp", "*.cc", "*.cxx"],
    )
    build_dir: str = ".cache/mkdocstrings-cpp"
    doxygen_bin: str = "doxygen"
    doxygen_timeout: int = 300
    recursive: bool = True
    project_name: str = "mkdocstrings-cpp"
    extra_doxygen: dict[str, Any] = field(default_factory=dict)
    options: CppOptions = field(default_factory=CppOptions)

    @classmethod
    def from_data(cls, **data: Any) -> CppConfig:
        """Build a handler config from mkdocs or Zensical plugin data."""
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise PluginError(f"Unknown C++ handler config key(s): {', '.join(unknown)}")

        values: dict[str, Any] = {}
        for name, value in data.items():
            if name in {"input", "file_patterns"}:
                values[name] = _as_list(value, field_name=name)
            elif name == "recursive":
                values[name] = _as_bool(value, field_name=name)
            elif name == "extra_doxygen":
                if not isinstance(value, dict):
                    raise PluginError("'extra_doxygen' must be a table/dictionary")
                values[name] = dict(value)
            elif name == "options":
                if not isinstance(value, dict):
                    raise PluginError("'options' must be a table/dictionary")
                values[name] = CppOptions.from_data(**value)
            else:
                values[name] = str(value)

        config = cls(**values)
        if not config.input:
            raise PluginError("C++ handler config requires at least one 'input' path")
        if not config.file_patterns:
            raise PluginError("C++ handler config requires at least one 'file_patterns' entry")
        return config

    def resolve_input_paths(self, base_dir: Path) -> list[Path]:
        """Resolve configured input paths against the config file directory."""
        return [
            path if (path := Path(item)).is_absolute() else (base_dir / path).resolve()
            for item in self.input
        ]

    def resolve_build_dir(self, base_dir: Path) -> Path:
        """Resolve the Doxygen cache directory."""
        path = Path(self.build_dir)
        return path if path.is_absolute() else (base_dir / path).resolve()
