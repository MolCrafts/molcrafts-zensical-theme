"""Template helpers for mkdocstrings-cpp."""

from __future__ import annotations

from collections.abc import Iterable

from mkdocstrings_handlers.cpp._internal.config import CppOptions
from mkdocstrings_handlers.cpp._internal.parser import CppObject


def do_visible_children(
    children: Iterable[CppObject],
    config: CppOptions,
    apply_members: bool = False,
) -> list[CppObject]:
    """Filter and order children for rendering."""
    result = [
        child
        for child in children
        if _is_visible(child, config) and _is_selected_member(child, config, apply_members)
    ]
    if config.members_order == "alphabetical":
        result.sort(key=lambda child: (child.name.casefold(), child.qualified_name.casefold()))
    return result


def _is_visible(child: CppObject, config: CppOptions) -> bool:
    if child.protection == "private" and not config.show_private:
        return False
    return not (child.protection == "protected" and not config.show_protected)


def _is_selected_member(child: CppObject, config: CppOptions, apply_members: bool) -> bool:
    if not apply_members or config.members is None:
        return True
    aliases = {
        child.name,
        child.qualified_name,
        child.qualified_name.rsplit("::", 1)[-1],
    }
    return any(member in aliases for member in config.members)
