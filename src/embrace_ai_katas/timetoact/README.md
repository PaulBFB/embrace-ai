# TimeToAct DocumentAI Parser

A Python parser for the TimeToAct DocumentAI specification - a structured document format that can describe contracts, procedures, or any business document in a way that can be loaded into AI Assistants.

## Installation

This parser is part of the embrace-ai project. Ensure you have the project dependencies installed:

```bash
uv sync
```

## Usage

### As a Python Module

```python
from src.embrace_ai_katas.timetoact import parse

# Parse a TimeToAct document
text = """
<head>My Document</head>
Content goes here

<dict sep=":">
Key: Value
</dict>
"""

result = parse(text)
print(result.model_dump_json(indent=2))
```

### Command Line Interface

The parser includes a CLI with several commands:

#### Parse a file to JSON
```bash
python -m src.embrace_ai_katas.timetoact parse-file input.txt
python -m src.embrace_ai_katas.timetoact parse-file input.txt -o output.json
python -m src.embrace_ai_katas.timetoact parse-file input.txt --compact  # Compact JSON
```

#### Validate a document
```bash
python -m src.embrace_ai_katas.timetoact validate input.txt
```

#### Run tests
```bash
python -m src.embrace_ai_katas.timetoact test data/timetoact_tests/
```

## Document Format

### Basic Structure

Every TimeToAct document is parsed into a root `Block` with optional head and body content:

```
<head>Document Title</head>
This is the document content.
```

### Headers

Use `<head>` tags to add titles to blocks:

```
<head>Section Title</head>
Section content here
```

### Blocks

Create nested structures with `<block>` tags:

```
<block>
<head>Chapter 1</head>
Chapter content
</block>
```

### Dictionaries

Key-value pairs with customizable separators:

```
<dict sep=":">
Name: John Doe
Age: 30
</dict>

<dict sep="=">
key1=value1
key2=value2
</dict>
```

### Lists

#### Ordered Lists
```
<list kind=".">
1. First item
2. Second item
2.1. Sub-item
2.2. Another sub-item
3. Third item
</list>
```

#### Unordered Lists
```
<list kind="*">
• Main point
• Another point
o Sub-point
• Final point
</list>
```

### Mixed Content

Lists can contain additional content:

```
<list kind=".">
1. First item
Additional text for the first item

<dict>
metadata: value
</dict>

2. Second item
</list>
```

## API Reference

### `parse(text: str) -> Block`

Parse a TimeToAct document string into a Block structure.

**Parameters:**
- `text`: The document text to parse

**Returns:**
- `Block`: The parsed document structure

**Raises:**
- `ParseError`: If the document is malformed

### Data Models

#### `Block`
- `kind`: Always "block"
- `number`: Optional section number (e.g., "1.2")
- `head`: Optional heading text
- `body`: List of content (strings, blocks, dictionaries, lists)

#### `Dictionary`
- `kind`: Always "dict"
- `items`: Dict[str, str] of key-value pairs

#### `ListBlock`
- `kind`: Always "list"
- `items`: List[Block] of list items

## Error Handling

The parser provides detailed error messages with line and column information:

```python
try:
    result = parse(malformed_text)
except ParseError as e:
    print(f"Error at line {e.line}, column {e.column}: {e}")
```

## Examples

### Complete Example

```python
from src.embrace_ai_katas.timetoact import parse

document = """
<head>Project Plan</head>
This document outlines our project plan.

<block>
<head>Overview</head>
Project description and goals.

<dict sep=":">
Start Date: 2024-01-01
End Date: 2024-12-31
Budget: $100,000
</dict>
</block>

<block>
<head>Tasks</head>
<list kind=".">
1. Planning Phase
1.1. Requirements gathering
1.2. Design documents
2. Implementation Phase
2.1. Backend development
2.2. Frontend development
3. Testing Phase
</list>
</block>
"""

result = parse(document)

# Access parsed data
print(f"Title: {result.head}")
print(f"Number of sections: {len(result.body)}")

# Convert to JSON
import json
json_output = json.dumps(result.model_dump(), indent=2)
print(json_output)
```

## Testing

Run the test suite:

```bash
uv run pytest tests/test_timetoact/
```

Run with coverage:

```bash
make test
```

## Development

### Code Quality

Format code:
```bash
make format
```

Type checking:
```bash
make mypy
```

### Project Structure

```
src/embrace_ai_katas/timetoact/
├── __init__.py       # Public API
├── models.py         # Pydantic data models
├── tokenizer.py      # Tokenization logic
├── parser.py         # Parsing logic
├── cli.py            # CLI interface
└── README.md         # This file
```