"""Pydantic models for TimeToAct DocumentAI parser."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

ContentNode = Union[str, "Block", "ListBlock", "Dictionary"]


class Dictionary(BaseModel):
    """A distinct dictionary structure for key-value pairs."""

    kind: Literal["dict"]
    items: Dict[str, str] = Field(default_factory=dict)


class Block(BaseModel):
    """A general-purpose container for a 'section' or item.

    - 'number' can store a section number (e.g., "5", "5.1") if present
    - 'head' is an optional heading for the block.
    - 'body' can hold any mix of strings, sub-blocks, dictionaries
    """

    kind: Literal["block"]
    number: Optional[str] = None
    head: Optional[str] = None
    body: List[ContentNode] = Field(default_factory=list)


class ListBlock(BaseModel):
    """A container for a list of items, each item being a 'Block'."""

    kind: Literal["list"]
    items: List[Block] = Field(default_factory=list)


Block.model_rebuild()
