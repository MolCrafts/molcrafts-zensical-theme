"""mkdocstrings handler implementation for C++."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, ClassVar

from mkdocs.exceptions import PluginError
from mkdocstrings import BaseHandler, CollectorItem, HandlerOptions

from mkdocstrings_handlers.cpp._internal.config import CppConfig, CppOptions
from mkdocstrings_handlers.cpp._internal.doxygen import DoxygenRunner
from mkdocstrings_handlers.cpp._internal.parser import CppIndex, DoxygenXmlParser
from mkdocstrings_handlers.cpp._internal.rendering import do_visible_children


class CppHandler(BaseHandler):
    """C++ handler backed by Doxygen XML."""

    name: ClassVar[str] = "cpp"
    domain: ClassVar[str] = "cpp"
    enable_inventory: ClassVar[bool] = True
    fallback_theme: ClassVar[str] = "material"

    def __init__(self, config: CppConfig, base_dir: Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.base_dir = base_dir
        self.global_options = config.options
        self._runner = DoxygenRunner(config, base_dir)
        self._parser = DoxygenXmlParser()
        self._index: CppIndex | None = None

    def get_options(self, local_options: dict[str, Any]) -> HandlerOptions:
        """Merge global and local render options."""
        data = asdict(self.global_options)
        data.update(local_options)
        try:
            return CppOptions.from_data(**data)
        except PluginError:
            raise
        except Exception as error:
            raise PluginError(f"Invalid C++ handler options: {error}") from error

    def collect(self, identifier: str, options: CppOptions) -> CollectorItem:  # noqa: ARG002
        """Collect one C++ object from the Doxygen XML index."""
        return self._ensure_index().get(identifier)

    def render(self, data: CollectorItem, options: CppOptions, *, locale: str | None = None) -> str:
        """Render a collected C++ object."""
        template = self.env.get_template("object.html.jinja")
        return template.render(
            object=data,
            config=options,
            heading_level=options.heading_level,
            root=True,
            locale=locale or "en",
        )

    def get_aliases(self, identifier: str) -> tuple[str, ...]:
        """Return known aliases for autorefs."""
        if self._index is None:
            return ()
        return self._index.aliases_for(identifier)

    def update_env(self, config: Any) -> None:  # noqa: ARG002
        """Install Jinja helpers."""
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False
        self.env.filters["visible_children"] = do_visible_children

    def _ensure_index(self) -> CppIndex:
        if self._index is None:
            result = self._runner.ensure_xml()
            self._index = self._parser.parse(result.xml_dir)
        return self._index


def get_handler(handler_config: dict[str, Any], tool_config: Any, **kwargs: Any) -> CppHandler:
    """Return a configured C++ handler instance."""
    config_path = Path(getattr(tool_config, "config_file_path", None) or "./mkdocs.yml")
    base_dir = config_path.parent.resolve()
    return CppHandler(
        config=CppConfig.from_data(**handler_config),
        base_dir=base_dir,
        **kwargs,
    )
