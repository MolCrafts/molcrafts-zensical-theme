from __future__ import annotations

from pathlib import Path
from shutil import which

import pytest

from mkdocstrings_handlers.cpp._internal.config import CppConfig, CppOptions
from mkdocstrings_handlers.cpp._internal.doxygen import DoxygenRunner
from mkdocstrings_handlers.cpp._internal.handler import CppHandler
from mkdocstrings_handlers.cpp._internal.parser import CppObject, DoxygenXmlParser
from mkdocstrings_handlers.cpp._internal.rendering import do_visible_children


def test_parser_collects_templates_overloads_and_enum_values(tmp_path: Path) -> None:
    xml_dir = _write_xml_fixture(tmp_path)

    index = DoxygenXmlParser().parse(xml_dir)

    vector = index.get("demo::Vector")
    assert vector.kind == "class"
    assert vector.signature == "template <typename T, std::size_t N>\nclass demo::Vector"
    assert vector.template_parameters[0].description == "Scalar type."
    assert [child.qualified_name for child in vector.children] == ["demo::Vector::size"]

    dot = index.get("demo::dot")
    assert dot.kind == "function"
    assert dot.parameters[0].description == "Left vector."
    assert dot.return_description == "Dot product."

    overloads = index.get("demo::format")
    assert overloads.kind == "function_group"
    assert len(overloads.children) == 2
    assert {child.argsstring for child in overloads.children} == {"(int value)", "(double value)"}

    channel = index.get("demo::Channel")
    assert channel.signature == "enum class demo::Channel"
    assert [value.name for value in channel.enum_values] == ["Console", "Json"]


def test_parser_handles_cxx20_concept(tmp_path: Path) -> None:
    xml_dir = _write_xml_fixture(tmp_path)
    index = DoxygenXmlParser().parse(xml_dir)

    eq = index.get("demo::EqualityComparable")
    assert eq.kind == "concept"
    assert eq.signature == (
        "template <typename T>\n"
        "concept demo::EqualityComparable = requires(const T& a, const T& b)"
    )
    assert eq.template_parameters[0].name == "T"
    assert eq.template_parameters[0].description == "Candidate type."


def test_visible_children_filters_access_and_requested_members(tmp_path: Path) -> None:
    xml_dir = _write_xml_fixture(tmp_path)
    index = DoxygenXmlParser().parse(xml_dir)
    vector = index.get("demo::Vector")
    vector.children.append(
        CppObject(
            kind="function",
            name="hidden",
            qualified_name="demo::Vector::hidden",
            protection="private",
        ),
    )

    options = CppOptions(members=["size"], show_private=False)
    children = do_visible_children(vector.children, options, apply_members=True)

    assert [child.name for child in children] == ["size"]


def test_handler_uses_bundled_material_template_for_molcrafts_theme(tmp_path: Path) -> None:
    handler = CppHandler(
        config=CppConfig.from_data(input=[str(tmp_path)]),
        base_dir=tmp_path,
        theme="molcrafts",
        custom_templates=None,
        mdx=[],
        mdx_config={},
    )
    handler.update_env(None)

    template = handler.env.get_template("object.html.jinja")

    assert template.filename is not None
    assert template.filename.endswith("templates/material/object.html.jinja")
    assert ".cpp-object" in handler.extra_css


@pytest.mark.skipif(which("doxygen") is None, reason="Doxygen is not installed")
def test_doxygen_runner_parses_demo_fixture(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    config = CppConfig.from_data(
        input=[str(root / "examples/cpp/include")],
        file_patterns=["*.hpp"],
        build_dir=str(tmp_path / "doxygen"),
    )

    result = DoxygenRunner(config, root).ensure_xml()
    index = DoxygenXmlParser().parse(result.xml_dir)

    assert index.get("demo").kind == "namespace"
    assert index.get("demo::Vector").template_parameters[1].name == "N"
    assert index.get("demo::format").kind == "function_group"
    assert index.get("demo::Channel").enum_values[0].name == "Console"


def _write_xml_fixture(tmp_path: Path) -> Path:
    xml_dir = tmp_path / "xml"
    xml_dir.mkdir(parents=True, exist_ok=True)
    (xml_dir / "index.xml").write_text("<doxygenindex />", encoding="utf-8")
    (xml_dir / "namespacedemo.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<doxygen>
  <compounddef id="namespacedemo" kind="namespace">
    <compoundname>demo</compoundname>
    <briefdescription><para>Demo namespace.</para></briefdescription>
    <innerclass refid="classdemo_1_1Vector">demo::Vector</innerclass>
    <innerclass refid="conceptdemo_1_1EqualityComparable">demo::EqualityComparable</innerclass>
    <sectiondef kind="enum">
      <memberdef kind="enum" id="enum_channel" prot="public" strong="yes">
        <name>Channel</name>
        <briefdescription><para>Output channel.</para></briefdescription>
        <enumvalue id="enum_channel_console">
          <name>Console</name>
          <briefdescription><para>Terminal output.</para></briefdescription>
        </enumvalue>
        <enumvalue id="enum_channel_json">
          <name>Json</name>
          <briefdescription><para>JSON output.</para></briefdescription>
        </enumvalue>
      </memberdef>
    </sectiondef>
    <sectiondef kind="func">
      <memberdef kind="function" id="dot" prot="public">
        <templateparamlist>
          <param><type>typename</type><declname>T</declname></param>
          <param><type>std::size_t</type><declname>N</declname></param>
        </templateparamlist>
        <type>T</type>
        <definition>T demo::dot</definition>
        <argsstring>(const Vector&lt; T, N &gt; &amp;lhs,
        const Vector&lt; T, N &gt; &amp;rhs)</argsstring>
        <name>dot</name>
        <param><type>const Vector&lt; T, N &gt; &amp;</type><declname>lhs</declname></param>
        <param><type>const Vector&lt; T, N &gt; &amp;</type><declname>rhs</declname></param>
        <briefdescription><para>Compute a dot product.</para></briefdescription>
        <detaileddescription>
          <para>
            <parameterlist kind="param">
              <parameteritem>
                <parameternamelist><parametername>lhs</parametername></parameternamelist>
                <parameterdescription><para>Left vector.</para></parameterdescription>
              </parameteritem>
              <parameteritem>
                <parameternamelist><parametername>rhs</parametername></parameternamelist>
                <parameterdescription><para>Right vector.</para></parameterdescription>
              </parameteritem>
            </parameterlist>
            <simplesect kind="return"><para>Dot product.</para></simplesect>
          </para>
        </detaileddescription>
      </memberdef>
      <memberdef kind="function" id="format_int" prot="public">
        <type>std::string</type>
        <definition>std::string demo::format</definition>
        <argsstring>(int value)</argsstring>
        <name>format</name>
        <param><type>int</type><declname>value</declname></param>
      </memberdef>
      <memberdef kind="function" id="format_double" prot="public">
        <type>std::string</type>
        <definition>std::string demo::format</definition>
        <argsstring>(double value)</argsstring>
        <name>format</name>
        <param><type>double</type><declname>value</declname></param>
      </memberdef>
    </sectiondef>
  </compounddef>
</doxygen>
""",
        encoding="utf-8",
    )
    (xml_dir / "classdemo_1_1Vector.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<doxygen>
  <compounddef id="classdemo_1_1Vector" kind="class" prot="public">
    <compoundname>demo::Vector</compoundname>
    <templateparamlist>
      <param><type>typename</type><declname>T</declname></param>
      <param><type>std::size_t</type><declname>N</declname></param>
    </templateparamlist>
    <briefdescription><para>A fixed-size vector.</para></briefdescription>
    <detaileddescription>
      <para>
        <parameterlist kind="templateparam">
          <parameteritem>
            <parameternamelist><parametername>T</parametername></parameternamelist>
            <parameterdescription><para>Scalar type.</para></parameterdescription>
          </parameteritem>
          <parameteritem>
            <parameternamelist><parametername>N</parametername></parameternamelist>
            <parameterdescription><para>Extent.</para></parameterdescription>
          </parameteritem>
        </parameterlist>
      </para>
    </detaileddescription>
    <sectiondef kind="public-func">
      <memberdef kind="function" id="vector_size" prot="public" const="yes">
        <type>std::size_t</type>
        <definition>std::size_t demo::Vector&lt; T, N &gt;::size</definition>
        <argsstring>() const</argsstring>
        <name>size</name>
        <briefdescription><para>Return the extent.</para></briefdescription>
      </memberdef>
    </sectiondef>
  </compounddef>
</doxygen>
""",
        encoding="utf-8",
    )
    (xml_dir / "conceptdemo_1_1EqualityComparable.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<doxygen>
  <compounddef id="conceptdemo_1_1EqualityComparable" kind="concept" prot="public">
    <compoundname>demo::EqualityComparable</compoundname>
    <templateparamlist>
      <param><type>typename</type><declname>T</declname></param>
    </templateparamlist>
    <initializer>requires(const T&amp; a, const T&amp; b)</initializer>
    <briefdescription><para>Concept satisfied by types that are comparable with
    <computeroutput>operator==</computeroutput>.</para></briefdescription>
    <detaileddescription>
      <para>
        <parameterlist kind="templateparam">
          <parameteritem>
            <parameternamelist><parametername>T</parametername></parameternamelist>
            <parameterdescription><para>Candidate type.</para></parameterdescription>
          </parameteritem>
        </parameterlist>
      </para>
    </detaileddescription>
    <location file="demo/api.hpp" line="42" column="1"/>
  </compounddef>
</doxygen>
""",
        encoding="utf-8",
    )
    return xml_dir
