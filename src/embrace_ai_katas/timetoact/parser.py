"""Parser for TimeToAct DocumentAI format."""

import re
from typing import Iterator, List, Optional, Tuple, Union

from src.embrace_ai_katas.timetoact.models import (
    Block,
    ContentNode,
    Dictionary,
    ListBlock,
)
from src.embrace_ai_katas.timetoact.tokenizer import Token, Tokenizer, TokenType


class ParseError(Exception):
    """Parser error with line and column information."""

    def __init__(self, message: str, token: Token):
        self.line = token.line
        self.column = token.column
        super().__init__(f"{message} at line {token.line}, column {token.column}")


class Parser:
    """Parses tokens into TimeToAct document structure."""

    def __init__(self, tokens: Iterator[Token]):
        """Initialize parser with token stream."""
        self.tokens = tokens
        self.current: Token = Token(TokenType.EOF, "", 0, 0)  # Initialize with EOF
        self.peek_buffer: List[Token] = []
        self._advance()

    def parse(self) -> Block:
        """Parse tokens into a root Block."""
        root = Block(kind="block")

        # Check if the first element is a head tag
        if self._is_opening_tag("head"):
            root.head = self._parse_head()

        root.body = self._parse_content()
        return root

    def _parse_content(self, until_tag: Optional[str] = None) -> List[ContentNode]:
        """Parse content until EOF or closing tag."""
        content: List[ContentNode] = []
        current_text: List[str] = []

        while self.current.type != TokenType.EOF:
            if until_tag and self._is_closing_tag(until_tag):
                break

            if self._is_opening_tag("head"):
                # Head tags within content should not happen if properly consumed at block level
                # Skip to avoid adding as text
                raise ParseError("Unexpected head tag in content", self.current)
            elif self._is_opening_tag("block"):
                self._flush_text(current_text, content)
                content.append(self._parse_block())
            elif self._is_opening_tag("dict"):
                self._flush_text(current_text, content)
                content.append(self._parse_dict())
            elif self._is_opening_tag("list"):
                self._flush_text(current_text, content)
                content.append(self._parse_list())
            elif self.current.type == TokenType.TEXT:
                current_text.append(self.current.value)
                self._advance()
            elif self.current.type == TokenType.NEWLINE:
                current_text.append("\n")
                self._advance()
            else:
                self._advance()

        self._flush_text(current_text, content)
        return content

    def _parse_head(self) -> str:
        """Parse head content."""
        self._expect_tag("head", is_closing=False)
        head_text = []

        while not self._is_closing_tag("head"):
            if self.current.type == TokenType.TEXT:
                head_text.append(self.current.value)
            elif self.current.type == TokenType.EOF:
                raise ParseError("Unexpected EOF in head tag", self.current)
            self._advance()

        self._expect_tag("head", is_closing=True)
        return "".join(head_text).strip()

    def _parse_block(self) -> Block:
        """Parse a block element."""
        self._expect_tag("block", is_closing=False)
        block = Block(kind="block")

        # Skip any newlines after the opening block tag
        while self.current.type == TokenType.NEWLINE:
            self._advance()

        # Check if the first element in the block is a head tag
        if self._is_opening_tag("head"):
            block.head = self._parse_head()

        block.body = self._parse_content(until_tag="block")
        self._expect_tag("block", is_closing=True)
        return block

    def _parse_dict(self) -> Dictionary:
        """Parse a dictionary element."""
        tag_token = self.current
        self._expect_tag("dict", is_closing=False)

        separator = ":"
        if tag_token.attributes and "sep" in tag_token.attributes:
            separator = tag_token.attributes["sep"]

        dictionary = Dictionary(kind="dict")
        lines = []
        current_line = []

        while not self._is_closing_tag("dict"):
            if self.current.type == TokenType.TEXT:
                current_line.append(self.current.value)
            elif self.current.type == TokenType.NEWLINE:
                if current_line:
                    lines.append("".join(current_line).strip())
                    current_line = []
            elif self.current.type == TokenType.EOF:
                raise ParseError("Unexpected EOF in dict tag", self.current)
            self._advance()

        if current_line:
            lines.append("".join(current_line).strip())

        for line in lines:
            if line:
                if separator in line:
                    key, value = line.split(separator, 1)
                    dictionary.items[key.strip()] = value.strip()
                else:
                    dictionary.items[line.strip()] = ""

        self._expect_tag("dict", is_closing=True)
        return dictionary

    def _parse_list(self) -> Union[ListBlock, Block]:
        """Parse a list element."""
        tag_token = self.current
        self._expect_tag("list", is_closing=False)

        list_kind = "."
        if tag_token.attributes and "kind" in tag_token.attributes:
            list_kind = tag_token.attributes["kind"]

        # Collect the entire content as text first
        content_parts = []
        while not self._is_closing_tag("list"):
            if self.current.type == TokenType.EOF:
                raise ParseError("Unexpected EOF in list tag", self.current)
            if self.current.type == TokenType.TEXT:
                content_parts.append(self.current.value)
            elif self.current.type == TokenType.NEWLINE:
                content_parts.append("\n")
            elif self.current.type == TokenType.TAG_OPEN:
                content_parts.append(self.current.value)
            elif self.current.type == TokenType.TAG_CLOSE:
                content_parts.append(self.current.value)
            self._advance()

        self._expect_tag("list", is_closing=True)

        # Reconstruct the content and parse it
        list_content = "".join(content_parts)
        lines = list_content.strip().split("\n")

        return self._process_list_lines(lines, list_kind)

    def _process_list_lines(
        self, lines: List[str], list_kind: str
    ) -> Union[ListBlock, Block]:
        """Process list lines into ListBlock structure."""
        if list_kind == ".":
            return self._process_ordered_list(lines)
        elif list_kind == "*":
            return self._process_unordered_list(lines)
        else:
            return ListBlock(kind="list", items=[])

    def _process_ordered_list(self, lines: List[str]) -> Union[ListBlock, Block]:
        """Process ordered list lines with auto-nesting."""
        root_items: List[Block] = []
        stack: List[Tuple[str, Block]] = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            match = re.match(r"^(\d+(?:\.\d+)*)\.\s+(.*)$", line)
            if match:
                number = match.group(1)
                text = match.group(2)

                item = Block(kind="block", number=number, head=text)
                level = number.count(".")

                while stack and stack[-1][0].count(".") >= level:
                    stack.pop()

                if not stack:
                    root_items.append(item)
                else:
                    parent = stack[-1][1]
                    if parent.body and isinstance(parent.body[-1], ListBlock):
                        parent.body[-1].items.append(item)
                    else:
                        sub_list = ListBlock(kind="list", items=[item])
                        parent.body.append(sub_list)

                stack.append((number, item))
                i += 1
            else:
                if stack:
                    # Check if this line contains structured content like <dict>
                    if "<dict" in line:
                        # Collect all lines for the dictionary
                        dict_lines = [line]
                        j = i + 1
                        while j < len(lines) and "</dict>" not in dict_lines[-1]:
                            dict_lines.append(lines[j])
                            j += 1

                        # Parse the dictionary content
                        dict_text = "\n".join(dict_lines)
                        sub_tokenizer = Tokenizer(dict_text)
                        sub_parser = Parser(sub_tokenizer.tokenize())
                        parsed = sub_parser.parse()

                        # Add parsed content to the current item
                        if parsed.body:
                            stack[-1][1].body.extend(parsed.body)

                        # Skip the processed lines
                        i = j
                    else:
                        stack[-1][1].body.append(line)
                        i += 1
                else:
                    i += 1

        return ListBlock(kind="list", items=root_items)

    def _process_unordered_list(self, lines: List[str]) -> ListBlock:
        """Process unordered list lines."""
        items = []
        current_item: Optional[Block] = None

        for line in lines:
            if not line.strip():
                continue

            if line.strip().startswith("• "):
                if current_item:
                    items.append(current_item)
                text = line.strip()[2:].strip()
                current_item = Block(kind="block", head=text)
            elif line.strip().startswith("o ") and current_item:
                text = line.strip()[2:].strip()
                sub_item = Block(kind="block", head=text)
                if current_item.body and isinstance(current_item.body[-1], ListBlock):
                    current_item.body[-1].items.append(sub_item)
                else:
                    sub_list = ListBlock(kind="list", items=[sub_item])
                    current_item.body.append(sub_list)
            elif current_item:
                current_item.body.append(line.strip())

        if current_item:
            items.append(current_item)

        return ListBlock(kind="list", items=items)

    def _flush_text(self, text_buffer: List[str], content: List[ContentNode]) -> None:
        """Flush accumulated text to content list."""
        if not text_buffer:
            return

        text = "".join(text_buffer).strip()
        if text:
            paragraphs = text.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if para:
                    content.append(para)

        text_buffer.clear()

    def _is_opening_tag(self, tag_name: str) -> bool:
        """Check if current token is an opening tag."""
        return (
            self.current.type == TokenType.TAG_OPEN
            and self.current.tag_name == tag_name
        )

    def _is_closing_tag(self, tag_name: str) -> bool:
        """Check if current token is a closing tag."""
        return (
            self.current.type == TokenType.TAG_CLOSE
            and self.current.tag_name == tag_name
        )

    def _expect_tag(self, tag_name: str, is_closing: bool) -> None:
        """Expect a specific tag, raise error if not found."""
        expected_type = TokenType.TAG_CLOSE if is_closing else TokenType.TAG_OPEN
        tag_type = "closing" if is_closing else "opening"

        if self.current.type != expected_type or self.current.tag_name != tag_name:
            raise ParseError(f"Expected {tag_type} {tag_name} tag", self.current)

        self._advance()

    def _advance(self) -> None:
        """Advance to next token."""
        try:
            self.current = next(self.tokens)
        except StopIteration:
            self.current = Token(TokenType.EOF, "", 0, 0)


def parse(text: str) -> Block:
    """Parse TimeToAct document text into Block structure."""
    tokenizer = Tokenizer(text)
    parser = Parser(tokenizer.tokenize())
    return parser.parse()
