from abc import ABC
from dataclasses import dataclass
from typing import Optional

@dataclass
class Query(ABC):
    """Base query class"""
    skip: int = 0
    limit: int = 100