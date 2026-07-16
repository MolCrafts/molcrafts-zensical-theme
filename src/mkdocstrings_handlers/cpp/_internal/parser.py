"""Doxygen XML parser used by the C++ handler."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from mkdocstrings import CollectionError

_SPACE_RE = re.compile(r"\s+")
_HTML_ID_RE = re.compile(r"[^0-9A-Za-z_.:-]+")
_FUNCTION_KINDS = {"function", "friend"}
_COMPOUND_KINDS = {"class", "struct", "union", "namespace", "file", "concept"}


def compact(text: str) -> str:
    """Normalize XML text whitespace."""
    return _SPACE_RE.sub(" ", text).strip()


@dataclass(slots=True)
class CppLocation:
    """Source location for a documented object."""

    file: str = ""
    line: int | None = None

    @classmethod
    def from_element(cls, element: Element | None) -> CppLocation | None:
        """Build a location from a Doxygen ``location`` element."""
        if element is None:
            return None
        line_text = element.get("line")
        return cls(
            file=element.get("file", ""),
            line=int(line_text) if line_text and line_text.isdigit() else None,
        )


@dataclass(slots=True)
class CppParameter:
    """Function parameter."""

    type: str
    name: str = ""
    default: str = ""
    description: str = ""

    @property
    def signature(self) -> str:
        """Render this parameter as C++ code."""
        result = self.type
        if self.name:
            result = f"{result} {self.name}" if result else self.name
        if self.default:
            result = f"{result} = {self.default}"
        return result


@dataclass(slots=True)
class CppTemplateParameter:
    """Template parameter."""

    type: str
    name: str = ""
    default: str = ""
    description: str = ""

    @property
    def signature(self) -> str:
        """Render this template parameter as C++ code."""
        result = self.type
        if self.name and self.name not in result.split():
            result = f"{result} {self.name}" if result else self.name
        if self.default:
            result = f"{result} = {self.default}"
        return result


@dataclass(slots=True)
class CppEnumValue:
    """Enum value."""

    name: str
    initializer: str = ""
    brief: str = ""
    description: str = ""


@dataclass(slots=True)
class CppObject:
    """Collected C++ object."""

    kind: str
    name: str
    qualified_name: str
    refid: str = ""
    brief: str = ""
    description: str = ""
    return_description: str = ""
    type: str = ""
    definition: str = ""
    argsstring: str = ""
    parameters: list[CppParameter] = field(default_factory=list)
    template_parameters: list[CppTemplateParameter] = field(default_factory=list)
    enum_values: list[CppEnumValue] = field(default_factory=list)
    children: list[CppObject] = field(default_factory=list)
    location: CppLocation | None = None
    protection: str = "public"
    static: bool = False
    constexpr: bool = False
    const: bool = False
    explicit: bool = False
    virtual: str = "non-virtual"
    strong: bool = False
    parent: str = ""

    @property
    def html_id(self) -> str:
        """Stable HTML id for headings."""
        source = (
            f"{self.qualified_name}-{self.refid}"
            if self.kind in _FUNCTION_KINDS and self.refid
            else self.qualified_name
        )
        slug = source.replace("::", "--")
        slug = slug.replace("<", "-").replace(">", "-")
        slug = _HTML_ID_RE.sub("-", slug).strip("-")
        return f"cpp-{slug or self.kind}"

    @property
    def has_docs(self) -> bool:
        """Whether this object has user-facing documentation text."""
        return bool(self.brief or self.description or self.return_description)

    @property
    def display_kind(self) -> str:
        """Human-readable object kind."""
        return self.kind.replace("_", " ")

    @property
    def signature(self) -> str:
        """Render a C++ signature for this object."""
        if self.kind == "function_group":
            return ""
        template = self.template_prefix
        if self.kind in {"class", "struct", "union"}:
            signature = f"{self.kind} {self.qualified_name}"
        elif self.kind == "concept":
            constraint = f" = {self.definition}" if self.definition else ""
            signature = f"concept {self.qualified_name}{constraint}"
        elif self.kind == "enum":
            signature = f"enum {'class ' if self.strong else ''}{self.qualified_name}"
        elif self.kind == "typedef":
            signature = self.definition or f"using {self.qualified_name} = {self.type}"
        elif self.kind == "variable":
            signature = self.definition or f"{self.type} {self.qualified_name}".strip()
        elif self.kind in _FUNCTION_KINDS:
            signature = self._function_signature()
        elif self.kind == "namespace":
            signature = f"namespace {self.qualified_name}"
        elif self.kind == "file":
            signature = self.name
        else:
            signature = self.definition or self.qualified_name
        return f"{template}\n{signature}" if template else signature

    @property
    def template_prefix(self) -> str:
        """Render the ``template <...>`` prefix, if present."""
        if not self.template_parameters:
            return ""
        params = ", ".join(param.signature for param in self.template_parameters)
        return f"template <{params}>"

    def _function_signature(self) -> str:
        if self.definition and self.argsstring:
            return f"{self.definition}{self.argsstring}"
        if self.definition:
            return self.definition

        prefix = "static " if self.static else ""
        suffix = " const" if self.const else ""
        parameters = ", ".join(parameter.signature for parameter in self.parameters)
        return f"{prefix}{self.type} {self.qualified_name}({parameters}){suffix}".strip()


@dataclass(slots=True)
class CppIndex:
    """Lookup index for parsed C++ objects."""

    objects: dict[str, CppObject]
    by_qualified_name: dict[str, list[CppObject]]
    by_short_name: dict[str, list[CppObject]]

    def get(self, identifier: str) -> CppObject:
        """Return a documented object by identifier."""
        identifier = identifier.removeprefix("cpp::")
        if identifier in self.objects:
            return self.objects[identifier]
        matches = self.by_qualified_name.get(identifier) or self.by_short_name.get(identifier) or []
        if not matches:
            raise CollectionError(f"C++ identifier '{identifier}' could not be found")
        if len(matches) == 1:
            return matches[0]
        if all(match.kind in _FUNCTION_KINDS for match in matches):
            first = matches[0]
            return CppObject(
                kind="function_group",
                name=first.name,
                qualified_name=first.qualified_name,
                children=matches,
                parent=first.parent,
            )
        names = ", ".join(match.qualified_name for match in matches)
        raise CollectionError(f"C++ identifier '{identifier}' is ambiguous: {names}")

    def aliases_for(self, identifier: str) -> tuple[str, ...]:
        """Return aliases known for an identifier."""
        try:
            obj = self.get(identifier)
        except CollectionError:
            return ()
        aliases = [obj.qualified_name]
        if obj.name != obj.qualified_name:
            aliases.append(obj.name)
        return tuple(dict.fromkeys(aliases))


class DoxygenXmlParser:
    """Parse a Doxygen XML directory into a C++ index."""

    def parse(self, xml_dir: Path) -> CppIndex:
        """Parse all compound XML files under ``xml_dir``."""
        if not (xml_dir / "index.xml").is_file():
            raise CollectionError(f"Doxygen XML index not found at {xml_dir / 'index.xml'}")

        objects: dict[str, CppObject] = {}
        pending_inner_refs: dict[str, list[str]] = {}

        for xml_file in sorted(xml_dir.glob("*.xml")):
            if xml_file.name == "index.xml":
                continue
            try:
                root = ET.parse(xml_file).getroot()
            except ET.ParseError as error:
                message = f"Could not parse Doxygen XML file {xml_file}: {error}"
                raise CollectionError(message) from error
            for compounddef in root.findall("compounddef"):
                compound = self._parse_compound(compounddef)
                if compound.kind not in _COMPOUND_KINDS:
                    continue
                objects.setdefault(compound.refid, compound)
                pending_inner_refs[compound.refid] = [
                    child.get("refid", "") for child in compounddef.findall("innerclass")
                ]
                pending_inner_refs[compound.refid].extend(
                    child.get("refid", "") for child in compounddef.findall("innernamespace")
                )
                for member in self._parse_members(compounddef, compound):
                    if member.refid not in objects:
                        objects[member.refid] = member
                        compound.children.append(member)

        self._attach_inner_objects(objects, pending_inner_refs)
        return self._build_index(objects.values())

    def _parse_compound(self, compounddef: Element) -> CppObject:
        kind = compounddef.get("kind", "")
        qualified_name = self._child_text(compounddef, "compoundname")
        name = qualified_name.rsplit("::", 1)[-1]
        template_params = self._parse_template_parameters(compounddef.find("templateparamlist"))
        tparam_docs = self._parameter_docs(compounddef, "templateparam")
        template_params = self._apply_template_docs(template_params, tparam_docs)

        return CppObject(
            kind=kind,
            name=name,
            qualified_name=qualified_name,
            refid=compounddef.get("id", qualified_name),
            brief=self._description(compounddef.find("briefdescription")),
            description=self._description(compounddef.find("detaileddescription")),
            definition=self._child_text(compounddef, "initializer"),
            template_parameters=template_params,
            location=CppLocation.from_element(compounddef.find("location")),
            protection=compounddef.get("prot", "public"),
        )

    def _parse_members(self, compounddef: Element, parent: CppObject) -> Iterable[CppObject]:
        for section in compounddef.findall("sectiondef"):
            for memberdef in section.findall("memberdef"):
                member = self._parse_member(memberdef, parent)
                if member is not None:
                    yield member

    def _parse_member(self, memberdef: Element, parent: CppObject) -> CppObject | None:
        kind = memberdef.get("kind", "")
        if kind not in {"function", "friend", "enum", "typedef", "variable"}:
            return None

        name = self._child_text(memberdef, "name")
        qualified_name = self._qualified_member_name(parent, name, memberdef)
        parameters = self._parse_parameters(memberdef.findall("param"))
        param_docs = self._parameter_docs(memberdef, "param")
        parameters = self._apply_parameter_docs(parameters, param_docs)
        template_params = self._parse_template_parameters(memberdef.find("templateparamlist"))
        tparam_docs = self._parameter_docs(memberdef, "templateparam")
        template_params = self._apply_template_docs(template_params, tparam_docs)

        return CppObject(
            kind=kind,
            name=name,
            qualified_name=qualified_name,
            refid=memberdef.get("id", qualified_name),
            brief=self._description(memberdef.find("briefdescription")),
            description=self._description(memberdef.find("detaileddescription")),
            return_description=self._return_description(memberdef),
            type=self._child_text(memberdef, "type"),
            definition=self._child_text(memberdef, "definition"),
            argsstring=self._child_text(memberdef, "argsstring"),
            parameters=parameters,
            template_parameters=template_params,
            enum_values=self._parse_enum_values(memberdef),
            location=CppLocation.from_element(memberdef.find("location")),
            protection=memberdef.get("prot", "public"),
            static=memberdef.get("static") == "yes",
            constexpr=memberdef.get("constexpr") == "yes",
            const=memberdef.get("const") == "yes",
            explicit=memberdef.get("explicit") == "yes",
            virtual=memberdef.get("virt", "non-virtual"),
            strong=memberdef.get("strong") == "yes",
            parent=parent.qualified_name,
        )

    def _qualified_member_name(self, parent: CppObject, name: str, memberdef: Element) -> str:
        if "::" in name:
            return name
        if parent.kind != "file":
            return f"{parent.qualified_name}::{name}" if parent.qualified_name else name
        definition = self._child_text(memberdef, "definition")
        extracted = self._extract_qualified_name_from_definition(definition, name)
        if extracted:
            return extracted
        return f"{parent.qualified_name}::{name}" if parent.qualified_name else name

    @staticmethod
    def _extract_qualified_name_from_definition(definition: str, name: str) -> str:
        if not definition or name not in definition:
            return ""
        before_args = definition.split("(", 1)[0]
        tokens = before_args.split()
        for token in reversed(tokens):
            cleaned = token.strip("*&")
            if cleaned.endswith(name) and "::" in cleaned:
                return cleaned
        return ""

    def _parse_parameters(self, elements: Iterable[Element]) -> list[CppParameter]:
        parameters: list[CppParameter] = []
        for element in elements:
            name = self._child_text(element, "declname") or self._child_text(element, "defname")
            array = self._child_text(element, "array")
            if array:
                name = f"{name}{array}"
            parameters.append(
                CppParameter(
                    type=self._child_text(element, "type"),
                    name=name,
                    default=self._child_text(element, "defval"),
                ),
            )
        return parameters

    def _parse_template_parameters(self, element: Element | None) -> list[CppTemplateParameter]:
        if element is None:
            return []
        parameters: list[CppTemplateParameter] = []
        for param in element.findall("param"):
            parameter_type = self._child_text(param, "type")
            name = self._child_text(param, "declname") or self._child_text(param, "defname")
            if not name and parameter_type:
                pieces = parameter_type.split()
                if len(pieces) > 1 and pieces[0] in {"class", "typename"}:
                    parameter_type, name = pieces[0], pieces[-1]
            parameters.append(
                CppTemplateParameter(
                    type=parameter_type,
                    name=name,
                    default=self._child_text(param, "defval"),
                ),
            )
        return parameters

    def _parse_enum_values(self, memberdef: Element) -> list[CppEnumValue]:
        values: list[CppEnumValue] = []
        for enumvalue in memberdef.findall("enumvalue"):
            values.append(
                CppEnumValue(
                    name=self._child_text(enumvalue, "name"),
                    initializer=self._child_text(enumvalue, "initializer"),
                    brief=self._description(enumvalue.find("briefdescription")),
                    description=self._description(enumvalue.find("detaileddescription")),
                ),
            )
        return values

    def _parameter_docs(self, element: Element, kind: str) -> dict[str, str]:
        docs: dict[str, str] = {}
        for parameter_list in element.findall(f".//parameterlist[@kind='{kind}']"):
            for item in parameter_list.findall("parameteritem"):
                description = self._description(item.find("parameterdescription"))
                for name_element in item.findall("parameternamelist/parametername"):
                    name = compact(self._inline_text(name_element))
                    if name:
                        docs[name] = description
        return docs

    def _return_description(self, element: Element) -> str:
        blocks: list[str] = []
        for simplesect in element.findall(".//simplesect[@kind='return']"):
            text = self._description(simplesect)
            if text:
                blocks.append(text)
        return "\n\n".join(blocks)

    @staticmethod
    def _apply_parameter_docs(
        parameters: list[CppParameter],
        docs: dict[str, str],
    ) -> list[CppParameter]:
        return [
            CppParameter(
                type=p.type,
                name=p.name,
                default=p.default,
                description=docs.get(p.name, p.description),
            )
            for p in parameters
        ]

    @staticmethod
    def _apply_template_docs(
        parameters: list[CppTemplateParameter],
        docs: dict[str, str],
    ) -> list[CppTemplateParameter]:
        return [
            CppTemplateParameter(
                type=p.type,
                name=p.name,
                default=p.default,
                description=docs.get(p.name, p.description),
            )
            for p in parameters
        ]

    def _description(self, element: Element | None) -> str:
        if element is None:
            return ""
        blocks: list[str] = []
        for child in element:
            if child.tag == "para":
                text = self._paragraph_text(child)
                if text:
                    blocks.append(text)
            elif child.tag == "programlisting":
                blocks.append(self._program_listing(child))
            elif child.tag in {"parameterlist", "simplesect"}:
                continue
            else:
                text = self._inline_text(child)
                if text:
                    blocks.append(text)
        return "\n\n".join(blocks)

    def _paragraph_text(self, element: Element) -> str:
        nested_blocks: list[str] = []
        inline = self._inline_text(element, skip_blocks=True)
        if inline:
            nested_blocks.append(inline)
        for child in element:
            if child.tag == "itemizedlist":
                nested_blocks.append(self._list_text(child, ordered=False))
            elif child.tag == "orderedlist":
                nested_blocks.append(self._list_text(child, ordered=True))
            elif child.tag == "programlisting":
                nested_blocks.append(self._program_listing(child))
        return "\n\n".join(block for block in nested_blocks if block)

    def _inline_text(self, element: Element, *, skip_blocks: bool = False) -> str:
        if skip_blocks and element.tag in {
            "parameterlist",
            "simplesect",
            "itemizedlist",
            "orderedlist",
            "programlisting",
        }:
            return compact(element.tail or "")

        parts: list[str] = []
        if element.text:
            parts.append(element.text)
        for child in element:
            if child.tag in {"parameterlist", "simplesect"}:
                rendered = ""
            elif child.tag == "ref":
                rendered = self._inline_text(child)
            elif child.tag == "computeroutput":
                rendered = f"`{compact(self._inline_text(child))}`"
            elif child.tag == "emphasis":
                rendered = f"*{compact(self._inline_text(child))}*"
            elif child.tag == "bold":
                rendered = f"**{compact(self._inline_text(child))}**"
            elif child.tag == "linebreak":
                rendered = "\n"
            elif child.tag == "sp":
                rendered = " "
            elif child.tag == "formula":
                rendered = child.text or ""
            elif child.tag == "programlisting":
                rendered = "" if skip_blocks else self._program_listing(child)
            elif child.tag in {"itemizedlist", "orderedlist"}:
                rendered = "" if skip_blocks else self._list_text(child, child.tag == "orderedlist")
            else:
                rendered = self._inline_text(child, skip_blocks=skip_blocks)
            if rendered:
                parts.append(rendered)
            if child.tail:
                parts.append(child.tail)
        return compact("".join(parts))

    def _list_text(self, element: Element, ordered: bool) -> str:
        lines: list[str] = []
        for index, item in enumerate(element.findall("listitem"), start=1):
            text = self._description(item) or self._inline_text(item)
            if not text:
                continue
            prefix = f"{index}." if ordered else "-"
            lines.append(f"{prefix} {text}")
        return "\n".join(lines)

    def _program_listing(self, element: Element) -> str:
        lines: list[str] = []
        for codeline in element.findall("codeline"):
            line = self._inline_text(codeline)
            lines.append(line.rstrip())
        code = "\n".join(lines).strip()
        return f"```cpp\n{code}\n```" if code else ""

    def _child_text(self, element: Element, child_name: str) -> str:
        child = element.find(child_name)
        return compact(self._inline_text(child)) if child is not None else ""

    @staticmethod
    def _attach_inner_objects(
        objects: dict[str, CppObject],
        pending_inner_refs: dict[str, list[str]],
    ) -> None:
        for parent_id, child_refs in pending_inner_refs.items():
            parent = objects.get(parent_id)
            if parent is None:
                continue
            existing = {child.refid for child in parent.children}
            for refid in child_refs:
                child = objects.get(refid)
                if child is not None and child.refid not in existing:
                    parent.children.append(child)
                    existing.add(child.refid)

    @staticmethod
    def _build_index(objects: Iterable[CppObject]) -> CppIndex:
        by_refid: dict[str, CppObject] = {}
        by_qualified: dict[str, list[CppObject]] = {}
        by_short: dict[str, list[CppObject]] = {}

        for obj in objects:
            key = obj.refid or obj.qualified_name
            by_refid[key] = obj
            by_qualified.setdefault(obj.qualified_name, []).append(obj)
            by_short.setdefault(obj.name, []).append(obj)

        return CppIndex(
            objects=by_refid,
            by_qualified_name=by_qualified,
            by_short_name=by_short,
        )
