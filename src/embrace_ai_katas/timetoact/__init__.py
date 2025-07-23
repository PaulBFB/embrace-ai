"""TimeToAct DocumentAI Parser

A parser for the TimeToAct DocumentAI specification that converts
structured text into JSON following predefined data models.
"""

from src.embrace_ai_katas.timetoact.models import Block, Dictionary, ListBlock
from src.embrace_ai_katas.timetoact.parser import parse

__all__ = ["parse", "Block", "Dictionary", "ListBlock"]
