"""抽取器抽象接口，让规则法和 LLM 法可以互换。"""
from abc import ABC, abstractmethod
from typing import List

from src.models import Paper, StructuredRecord


class BaseExtractor(ABC):
    name: str = "base"

    @abstractmethod
    def extract(self, paper: Paper) -> StructuredRecord:
        ...

    def extract_batch(self, papers: List[Paper]) -> List[StructuredRecord]:
        return [self.extract(p) for p in papers]
