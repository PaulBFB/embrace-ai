"""Tests for TimeToAct models."""

from src.embrace_ai_katas.timetoact.models import Block, Dictionary, ListBlock


def test_dictionary_creation():
    """Test Dictionary model creation."""
    dict_obj = Dictionary(kind="dict", items={"key1": "value1", "key2": "value2"})
    assert dict_obj.kind == "dict"
    assert dict_obj.items == {"key1": "value1", "key2": "value2"}


def test_block_creation():
    """Test Block model creation."""
    block = Block(kind="block", head="Test Block", body=["Some text"])
    assert block.kind == "block"
    assert block.head == "Test Block"
    assert block.body == ["Some text"]
    assert block.number is None


def test_block_with_number():
    """Test Block with section number."""
    block = Block(kind="block", number="1.2", head="Section 1.2")
    assert block.number == "1.2"
    assert block.head == "Section 1.2"


def test_listblock_creation():
    """Test ListBlock model creation."""
    item1 = Block(kind="block", head="Item 1")
    item2 = Block(kind="block", head="Item 2")
    list_block = ListBlock(kind="list", items=[item1, item2])
    assert list_block.kind == "list"
    assert len(list_block.items) == 2
    assert list_block.items[0].head == "Item 1"


def test_nested_content():
    """Test nested content structures."""
    inner_dict = Dictionary(kind="dict", items={"nested": "value"})
    inner_block = Block(kind="block", head="Inner", body=["Inner text"])
    outer_block = Block(
        kind="block", head="Outer", body=["Text", inner_dict, inner_block]
    )

    assert outer_block.kind == "block"
    assert len(outer_block.body) == 3
    assert isinstance(outer_block.body[0], str)
    assert isinstance(outer_block.body[1], Dictionary)
    assert isinstance(outer_block.body[2], Block)


def test_model_json_serialization():
    """Test JSON serialization of models."""
    block = Block(
        kind="block",
        head="Test",
        body=["Text", Dictionary(kind="dict", items={"key": "value"})],
    )
    json_data = block.model_dump()

    assert json_data["kind"] == "block"
    assert json_data["head"] == "Test"
    assert len(json_data["body"]) == 2
    assert json_data["body"][1]["kind"] == "dict"
