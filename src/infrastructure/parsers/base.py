from abc import ABC, abstractmethod
from src.infrastructure.agents.resume import OutResumeParse
from io import BytesIO
from typing import Union

type ParserInput = Union[BytesIO, str]

class BaseResumeParser(ABC):
    @abstractmethod
    async def extract_text(self, source: ParserInput) -> OutResumeParse:
        ...