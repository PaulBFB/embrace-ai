"""Test edge cases and error handling for TimeToAct parser."""

import pytest

from src.embrace_ai_katas.timetoact.parser import ParseError, parse


def test_unclosed_head_tag():
    """Test error on unclosed head tag."""
    with pytest.raises(ParseError) as exc_info:
        parse("<head>Title without closing tag")
    assert "EOF" in str(exc_info.value)


def test_unclosed_block_tag():
    """Test error on unclosed block tag."""
    with pytest.raises(ParseError) as exc_info:
        parse("<block>Content without closing")
    assert "Expected closing block tag" in str(exc_info.value)


def test_unclosed_dict_tag():
    """Test error on unclosed dict tag."""
    with pytest.raises(ParseError) as exc_info:
        parse("<dict>Key: Value")
    assert "EOF" in str(exc_info.value)


def test_unclosed_list_tag():
    """Test error on unclosed list tag."""
    with pytest.raises(ParseError) as exc_info:
        parse('<list kind=".">1. Item')
    assert "EOF" in str(exc_info.value)


def test_mismatched_closing_tag():
    """Test error on mismatched closing tags."""
    with pytest.raises(ParseError) as exc_info:
        parse("<block><head>Test</head></dict>")
    assert "Expected closing block tag" in str(exc_info.value)


def test_empty_document():
    """Test parsing completely empty document."""
    result = parse("")
    assert result.kind == "block"
    assert result.body == []
    assert result.head is None
    assert result.number is None


def test_whitespace_only_document():
    """Test parsing document with only whitespace."""
    result = parse("   \n\n   \t\n   ")
    assert result.kind == "block"
    assert result.body == []


def test_nested_blocks_deeply():
    """Test deeply nested blocks."""
    text = """<block>
<block>
<block>
<block>
Deep content
</block>
</block>
</block>
</block>"""
    result = parse(text)

    # Navigate to the deepest block
    current = result.body[0]
    depth = 0
    while current.body and isinstance(current.body[0], type(current)):
        current = current.body[0]
        depth += 1

    assert depth == 3
    assert current.body == ["Deep content"]


def test_empty_dictionary():
    """Test empty dictionary."""
    result = parse("<dict></dict>")
    assert len(result.body) == 1
    dict_obj = result.body[0]
    assert dict_obj.kind == "dict"
    assert dict_obj.items == {}


def test_dict_with_empty_values():
    """Test dictionary with keys but no values."""
    text = """<dict>
Key1:
Key2:
Key3:
</dict>"""
    result = parse(text)
    dict_obj = result.body[0]
    assert dict_obj.items == {"Key1": "", "Key2": "", "Key3": ""}


def test_dict_with_no_separator():
    """Test dictionary entries without separator."""
    text = """<dict>
JustAKey
Another Key Without Value
</dict>"""
    result = parse(text)
    dict_obj = result.body[0]
    assert dict_obj.items == {"JustAKey": "", "Another Key Without Value": ""}


def test_empty_list():
    """Test empty list."""
    result = parse('<list kind="."></list>')
    list_obj = result.body[0]
    assert list_obj.kind == "list"
    assert list_obj.items == []


def test_mixed_content_types():
    """Test document with all content types mixed."""
    text = """<head>Mixed Content Test</head>
Plain text here

<dict sep=":">
Key: Value
</dict>

<list kind=".">
1. Item
</list>

<block>
<head>Nested</head>
Nested content
</block>

Final text"""
    result = parse(text)

    assert result.head == "Mixed Content Test"
    assert len(result.body) == 5
    assert isinstance(result.body[0], str)
    assert result.body[1].kind == "dict"
    assert result.body[2].kind == "list"
    assert result.body[3].kind == "block"
    assert isinstance(result.body[4], str)


def test_unicode_content():
    """Test parsing with Unicode content."""
    text = """<head>Unicode 测试 🎉</head>
Content with émojis 🚀 and spëcial characters

<dict>
Key: Значение 值
Emoji🔑: Value🎯
</dict>"""
    result = parse(text)

    assert result.head == "Unicode 测试 🎉"
    assert "émojis 🚀" in result.body[0]
    dict_obj = result.body[1]
    assert "Значение 值" in dict_obj.items["Key"]
    assert dict_obj.items["Emoji🔑"] == "Value🎯"


def test_very_long_lines():
    """Test parsing with very long lines."""
    long_text = "A" * 10000
    result = parse(long_text)
    assert result.body[0] == long_text


def test_special_characters_in_dict_separator():
    """Test dictionary with special separator characters."""
    text = """<dict sep="::">
Key::Value
Another::Test
</dict>"""
    result = parse(text)
    dict_obj = result.body[0]
    assert dict_obj.items == {"Key": "Value", "Another": "Test"}


def test_list_with_no_items_matching_pattern():
    """Test list where no lines match the expected pattern."""
    text = """<list kind=".">
This is not a list item
Neither is this
</list>"""
    result = parse(text)
    list_obj = result.body[0]
    # These should be treated as body content of the list
    assert len(list_obj.items) == 0 or (
        len(list_obj.items) > 0 and list_obj.items[0].body
    )
