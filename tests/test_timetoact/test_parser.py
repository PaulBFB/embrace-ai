"""Tests for TimeToAct parser."""

import json

import pytest

from src.embrace_ai_katas.timetoact.models import Block, Dictionary, ListBlock
from src.embrace_ai_katas.timetoact.parser import ParseError, parse


def test_empty_document():
    """Test parsing empty document."""
    result = parse("")
    assert isinstance(result, Block)
    assert result.kind == "block"
    assert result.body == []
    assert result.head is None


def test_simple_text():
    """Test parsing simple text."""
    result = parse("Hello World")
    assert result.kind == "block"
    assert len(result.body) == 1
    assert result.body[0] == "Hello World"


def test_multiline_text():
    """Test parsing multiline text."""
    text = """Line 1
Line 2

Line 3"""
    result = parse(text)
    assert len(result.body) == 2
    assert result.body[0] == "Line 1\nLine 2"
    assert result.body[1] == "Line 3"


def test_head_tag():
    """Test parsing head tag."""
    text = """<head>Document Title</head>
Content here"""
    result = parse(text)
    assert result.head == "Document Title"
    assert result.body == ["Content here"]


def test_nested_block():
    """Test parsing nested blocks."""
    text = """<head>Outer</head>
Outer content
<block>
<head>Inner</head>
Inner content
</block>
More outer content"""
    result = parse(text)

    assert result.head == "Outer"
    assert len(result.body) == 3
    assert result.body[0] == "Outer content"
    assert isinstance(result.body[1], Block)
    assert result.body[1].head == "Inner"
    assert result.body[1].body == ["Inner content"]
    assert result.body[2] == "More outer content"


def test_dictionary_basic():
    """Test parsing basic dictionary."""
    text = """<dict>
Key1: Value1
Key2: Value2
</dict>"""
    result = parse(text)

    assert len(result.body) == 1
    dict_obj = result.body[0]
    assert isinstance(dict_obj, Dictionary)
    assert dict_obj.items == {"Key1": "Value1", "Key2": "Value2"}


def test_dictionary_custom_separator():
    """Test dictionary with custom separator."""
    text = """<dict sep="-">
Key1 - Value1
Key2 - Value2
</dict>"""
    result = parse(text)

    dict_obj = result.body[0]
    assert dict_obj.items == {"Key1": "Value1", "Key2": "Value2"}


def test_dictionary_empty_values():
    """Test dictionary with empty values."""
    text = """<dict>
Key1:
Key2: Value2
Key3
</dict>"""
    result = parse(text)

    dict_obj = result.body[0]
    assert dict_obj.items == {"Key1": "", "Key2": "Value2", "Key3": ""}


def test_ordered_list():
    """Test parsing ordered list."""
    text = """<list kind=".">
1. First item
2. Second item
3. Third item
</list>"""
    result = parse(text)

    assert len(result.body) == 1
    list_obj = result.body[0]
    assert isinstance(list_obj, ListBlock)
    assert len(list_obj.items) == 3
    assert list_obj.items[0].number == "1"
    assert list_obj.items[0].head == "First item"
    assert list_obj.items[1].number == "2"
    assert list_obj.items[1].head == "Second item"


def test_nested_ordered_list():
    """Test auto-detection of nested ordered lists."""
    text = """<list kind=".">
1. First item
2. Second item
2.1. Sub item one
2.2. Sub item two
3. Third item
</list>"""
    result = parse(text)

    list_obj = result.body[0]
    assert len(list_obj.items) == 3

    second_item = list_obj.items[1]
    assert second_item.number == "2"
    assert len(second_item.body) == 1
    assert isinstance(second_item.body[0], ListBlock)

    sub_list = second_item.body[0]
    assert len(sub_list.items) == 2
    assert sub_list.items[0].number == "2.1"
    assert sub_list.items[0].head == "Sub item one"


def test_unordered_list():
    """Test parsing unordered list."""
    text = """<list kind="*">
• First item
• Second item
o Sub item
• Third item
</list>"""
    result = parse(text)

    list_obj = result.body[0]
    assert len(list_obj.items) == 3
    assert list_obj.items[0].head == "First item"

    second_item = list_obj.items[1]
    assert second_item.head == "Second item"
    assert len(second_item.body) == 1
    assert isinstance(second_item.body[0], ListBlock)
    assert second_item.body[0].items[0].head == "Sub item"


def test_list_with_content():
    """Test list items with additional content."""
    text = """<list kind=".">
1. First item
Additional text for first item
2. Second item
<dict>
Key: Value
</dict>
</list>"""
    result = parse(text)

    list_obj = result.body[0]
    first_item = list_obj.items[0]
    assert first_item.head == "First item"
    assert first_item.body == ["Additional text for first item"]

    second_item = list_obj.items[1]
    assert second_item.head == "Second item"
    assert len(second_item.body) == 1
    assert isinstance(second_item.body[0], Dictionary)


def test_complex_nested_structure():
    """Test complex nested document structure."""
    text = """<head>Main Document</head>
Introduction text

<block>
<head>Section 1</head>
Section content

<dict>
Author: John Doe
Date: 2024-01-01
</dict>

<list kind=".">
1. Point one
2. Point two
</list>
</block>

Conclusion text"""
    result = parse(text)

    assert result.head == "Main Document"
    assert len(result.body) == 3
    assert result.body[0] == "Introduction text"

    section = result.body[1]
    assert isinstance(section, Block)
    assert section.head == "Section 1"
    assert len(section.body) == 3
    assert section.body[0] == "Section content"
    assert isinstance(section.body[1], Dictionary)
    assert isinstance(section.body[2], ListBlock)

    assert result.body[2] == "Conclusion text"


def test_unclosed_tag_error():
    """Test error handling for unclosed tags."""
    with pytest.raises(ParseError) as exc_info:
        parse("<head>Title")
    assert "EOF" in str(exc_info.value)


def test_mismatched_tag_error():
    """Test error handling for mismatched tags."""
    with pytest.raises(ParseError) as exc_info:
        parse("<block><head>Test</head></dict>")
    assert "Expected closing block tag" in str(exc_info.value)
