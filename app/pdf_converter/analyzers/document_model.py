from dataclasses import dataclass
from typing import List


@dataclass
class DocBlock:
    type: str
    content: str


@dataclass
class StructuredDocument:
    title: str
    blocks: List[DocBlock]
