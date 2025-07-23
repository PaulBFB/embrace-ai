"""Tests for TimeToAct tokenizer."""

from src.embrace_ai_katas.timetoact.tokenizer import Token, Tokenizer, TokenType


def test_simple_text_tokenization():
    """Test tokenization of simple text."""
    tokenizer = Tokenizer("Hello World")
    tokens = list(tokenizer.tokenize())

    assert len(tokens) == 2
    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Hello World"
    assert tokens[1].type == TokenType.EOF


def test_tag_tokenization():
    """Test tokenization of tags."""
    tokenizer = Tokenizer("<head>Title</head>")
    tokens = list(tokenizer.tokenize())

    assert len(tokens) == 4
    assert tokens[0].type == TokenType.TAG_OPEN
    assert tokens[0].tag_name == "head"
    assert tokens[1].type == TokenType.TEXT
    assert tokens[1].value == "Title"
    assert tokens[2].type == TokenType.TAG_CLOSE
    assert tokens[2].tag_name == "head"


def test_tag_with_attributes():
    """Test tokenization of tags with attributes."""
    tokenizer = Tokenizer('<dict sep=":">')
    tokens = list(tokenizer.tokenize())

    assert tokens[0].type == TokenType.TAG_OPEN
    assert tokens[0].tag_name == "dict"
    assert tokens[0].attributes == {"sep": ":"}


def test_multiple_attributes():
    """Test tags with multiple attributes."""
    tokenizer = Tokenizer('<list kind="." style="ordered">')
    tokens = list(tokenizer.tokenize())

    assert tokens[0].attributes == {"kind": ".", "style": "ordered"}


def test_newline_tokenization():
    """Test newline handling."""
    tokenizer = Tokenizer("Line 1\nLine 2\r\nLine 3")
    tokens = list(tokenizer.tokenize())

    text_tokens = [t for t in tokens if t.type == TokenType.TEXT]
    newline_tokens = [t for t in tokens if t.type == TokenType.NEWLINE]

    assert len(text_tokens) == 3
    assert len(newline_tokens) == 2
    assert text_tokens[0].value == "Line 1"
    assert text_tokens[1].value == "Line 2"
    assert text_tokens[2].value == "Line 3"


def test_mixed_content():
    """Test mixed content tokenization."""
    content = """<head>Title</head>
Some text
<block>
Inner content
</block>"""
    tokenizer = Tokenizer(content)
    tokens = list(tokenizer.tokenize())

    tag_opens = [t for t in tokens if t.type == TokenType.TAG_OPEN]
    tag_closes = [t for t in tokens if t.type == TokenType.TAG_CLOSE]

    assert len(tag_opens) == 2
    assert len(tag_closes) == 2
    assert tag_opens[0].tag_name == "head"
    assert tag_opens[1].tag_name == "block"


def test_position_tracking():
    """Test line and column position tracking."""
    tokenizer = Tokenizer("Line 1\nLine 2")
    tokens = list(tokenizer.tokenize())

    assert tokens[0].line == 1
    assert tokens[0].column == 1
    assert tokens[2].line == 2
    assert tokens[2].column == 1
