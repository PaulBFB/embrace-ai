"""Tokenizer for TimeToAct DocumentAI parser."""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Iterator, Optional


class TokenType(Enum):
    """Token types for the TimeToAct parser."""

    TAG_OPEN = auto()
    TAG_CLOSE = auto()
    TEXT = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    """A token with type, value, and position information."""

    type: TokenType
    value: str
    line: int
    column: int
    tag_name: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None


class Tokenizer:
    """Tokenizes TimeToAct document format into tokens."""

    TAG_PATTERN = re.compile(r"<(/?)(\w+)(\s+[^>]+)?>")
    ATTR_PATTERN = re.compile(r'(\w+)="([^"]*)"')

    def __init__(self, text: str):
        """Initialize tokenizer with input text."""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> Iterator[Token]:
        """Generate tokens from the input text."""
        while self.pos < len(self.text):
            if self._at_tag():
                yield self._read_tag()
            elif self._at_newline():
                yield self._read_newline()
            else:
                yield self._read_text()

        yield Token(TokenType.EOF, "", self.line, self.column)

    def _at_tag(self) -> bool:
        """Check if current position is at a tag."""
        return self.text[self.pos] == "<" and bool(
            self.TAG_PATTERN.match(self.text, self.pos)
        )

    def _at_newline(self) -> bool:
        """Check if current position is at a newline."""
        return self.text[self.pos] in "\r\n"

    def _read_tag(self) -> Token:
        """Read a tag token."""
        match = self.TAG_PATTERN.match(self.text, self.pos)
        if not match:
            raise ValueError(f"Invalid tag at line {self.line}, column {self.column}")

        full_tag = match.group(0)
        is_close = bool(match.group(1))
        tag_name = match.group(2)
        attrs_str = match.group(3)

        token_type = TokenType.TAG_CLOSE if is_close else TokenType.TAG_OPEN
        attributes = self._parse_attributes(attrs_str) if attrs_str else None

        token = Token(
            type=token_type,
            value=full_tag,
            line=self.line,
            column=self.column,
            tag_name=tag_name,
            attributes=attributes,
        )

        self._advance(len(full_tag))
        return token

    def _read_newline(self) -> Token:
        """Read a newline token."""
        token = Token(TokenType.NEWLINE, "\n", self.line, self.column)

        if (
            self.text[self.pos] == "\r"
            and self.pos + 1 < len(self.text)
            and self.text[self.pos + 1] == "\n"
        ):
            self._advance(2)
        else:
            self._advance(1)

        return token

    def _read_text(self) -> Token:
        """Read text until next tag or newline."""
        start_pos = self.pos
        start_column = self.column

        while (
            self.pos < len(self.text) and not self._at_tag() and not self._at_newline()
        ):
            self._advance(1)

        text = self.text[start_pos : self.pos]
        return Token(TokenType.TEXT, text, self.line, start_column)

    def _parse_attributes(self, attrs_str: str) -> Dict[str, str]:
        """Parse attributes from attribute string."""
        attrs = {}
        for match in self.ATTR_PATTERN.finditer(attrs_str):
            key = match.group(1)
            value = match.group(2)
            attrs[key] = value
        return attrs

    def _advance(self, count: int = 1) -> None:
        """Advance position and track line/column."""
        for _ in range(count):
            if self.pos < len(self.text):
                if self.text[self.pos] == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
