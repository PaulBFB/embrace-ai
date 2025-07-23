"""Test compliance with TimeToAct specification examples."""

import json

from src.embrace_ai_katas.timetoact.parser import parse


def assert_json_equal(result, expected):
    """Assert that result matches expected JSON structure."""
    result_json = result.model_dump()
    assert result_json == expected


def test_spec_empty_text():
    """Test: Empty text → Empty block."""
    result = parse("")
    assert_json_equal(
        result, {"kind": "block", "number": None, "head": None, "body": []}
    )


def test_spec_plain_body_text():
    """Test: Plain body text → Block with body array of strings."""
    result = parse("This is plain text")
    assert_json_equal(
        result,
        {"kind": "block", "number": None, "head": None, "body": ["This is plain text"]},
    )


def test_spec_multiline_text():
    """Test: Multiline text with paragraph breaks."""
    text = """First paragraph here

Second paragraph here"""
    result = parse(text)
    assert_json_equal(
        result,
        {
            "kind": "block",
            "number": None,
            "head": None,
            "body": ["First paragraph here", "Second paragraph here"],
        },
    )


def test_spec_header():
    """Test: Headers → Block with head field."""
    text = """<head>Test Document</head>
Content goes here"""
    result = parse(text)
    assert_json_equal(
        result,
        {
            "kind": "block",
            "number": None,
            "head": "Test Document",
            "body": ["Content goes here"],
        },
    )


def test_spec_nested_blocks():
    """Test: Nested blocks → Hierarchical block structure."""
    text = """<head>AI Coding Kata</head>
Let's get started with the kata
<block>
<head>Preface</head>
Here is a little story
</block>"""
    result = parse(text)
    assert_json_equal(
        result,
        {
            "kind": "block",
            "number": None,
            "head": "AI Coding Kata",
            "body": [
                "Let's get started with the kata",
                {
                    "kind": "block",
                    "number": None,
                    "head": "Preface",
                    "body": ["Here is a little story"],
                },
            ],
        },
    )


def test_spec_dictionary_basic():
    """Test: Dictionaries → Dict objects with items."""
    text = """<dict sep=":">
Key One: Value One
Key Two: Value Two
Key Three: Value Three
</dict>"""
    result = parse(text)
    assert_json_equal(
        result,
        {
            "kind": "block",
            "number": None,
            "head": None,
            "body": [
                {
                    "kind": "dict",
                    "items": {
                        "Key One": "Value One",
                        "Key Two": "Value Two",
                        "Key Three": "Value Three",
                    },
                }
            ],
        },
    )


def test_spec_dictionary_custom_separator():
    """Test: Dictionary with custom separator."""
    text = """<dict sep="-">
Name - John Doe
Age - 30
City - New York
</dict>"""
    result = parse(text)
    dict_obj = result.body[0]
    assert dict_obj.items == {"Name": "John Doe", "Age": "30", "City": "New York"}


def test_spec_ordered_list():
    """Test: Ordered lists → ListBlock with numbered items."""
    text = """<list kind=".">
1. First item
2. Second item
3. Third item
</list>"""
    result = parse(text)
    list_obj = result.body[0]
    assert list_obj.kind == "list"
    assert len(list_obj.items) == 3
    assert list_obj.items[0].number == "1"
    assert list_obj.items[0].head == "First item"
    assert list_obj.items[1].number == "2"
    assert list_obj.items[1].head == "Second item"
    assert list_obj.items[2].number == "3"
    assert list_obj.items[2].head == "Third item"


def test_spec_nested_ordered_list():
    """Test: Auto-detection of nested lists."""
    text = """<list kind=".">
1. First
2. Second
2.1. Subitem 1
2.2. Subitem 2
</list>"""
    result = parse(text)
    list_obj = result.body[0]

    assert len(list_obj.items) == 2
    assert list_obj.items[0].number == "1"
    assert list_obj.items[0].head == "First"

    second_item = list_obj.items[1]
    assert second_item.number == "2"
    assert second_item.head == "Second"
    assert len(second_item.body) == 1

    sub_list = second_item.body[0]
    assert sub_list.kind == "list"
    assert len(sub_list.items) == 2
    assert sub_list.items[0].number == "2.1"
    assert sub_list.items[0].head == "Subitem 1"
    assert sub_list.items[1].number == "2.2"
    assert sub_list.items[1].head == "Subitem 2"


def test_spec_unordered_list():
    """Test: Unordered lists → ListBlock with bulleted items."""
    text = """<list kind="*">
• First
• Second
o Nested under second
• Third
</list>"""
    result = parse(text)
    list_obj = result.body[0]

    assert len(list_obj.items) == 3
    assert list_obj.items[0].head == "First"

    second_item = list_obj.items[1]
    assert second_item.head == "Second"
    assert len(second_item.body) == 1

    nested_list = second_item.body[0]
    assert nested_list.kind == "list"
    assert nested_list.items[0].head == "Nested under second"

    assert list_obj.items[2].head == "Third"


def test_spec_list_with_mixed_content():
    """Test: Lists with additional content."""
    text = """<list kind=".">
1. First
First body
2. Second
Some more text
<dict sep=":">
Key: Value
Another Key: Another Value
</dict>
</list>"""
    result = parse(text)
    list_obj = result.body[0]

    first_item = list_obj.items[0]
    assert first_item.number == "1"
    assert first_item.head == "First"
    assert first_item.body == ["First body"]

    second_item = list_obj.items[1]
    assert second_item.number == "2"
    assert second_item.head == "Second"
    assert len(second_item.body) == 2
    assert second_item.body[0] == "Some more text"

    dict_obj = second_item.body[1]
    assert dict_obj.kind == "dict"
    assert dict_obj.items == {"Key": "Value", "Another Key": "Another Value"}


def test_spec_complex_document():
    """Test: Complex nested document structure."""
    text = """<head>TimeToAct Example</head>
This is an example document

<block>
<head>Introduction</head>
Welcome to TimeToAct

<dict sep=":">
Version: 1.0
Author: Test Suite
</dict>
</block>

<block>
<head>Features</head>
<list kind=".">
1. Blocks
2. Lists
2.1. Ordered
2.2. Unordered
3. Dictionaries
</list>
</block>"""
    result = parse(text)

    assert result.head == "TimeToAct Example"
    assert len(result.body) == 3
    assert result.body[0] == "This is an example document"

    intro_block = result.body[1]
    assert intro_block.kind == "block"
    assert intro_block.head == "Introduction"
    assert intro_block.body[0] == "Welcome to TimeToAct"
    assert intro_block.body[1].kind == "dict"

    features_block = result.body[2]
    assert features_block.head == "Features"
    assert len(features_block.body) == 1

    list_obj = features_block.body[0]
    assert list_obj.kind == "list"
    assert len(list_obj.items) == 3
    assert list_obj.items[1].body[0].kind == "list"
