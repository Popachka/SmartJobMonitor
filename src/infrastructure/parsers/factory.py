from .pdf_parser import PDFParser
from .base import BaseResumeParser
class ParserFactory:
    _extension_map = {
        '.pdf': PDFParser,
    }
    
    @classmethod
    def get_parser_by_extension(cls, file_name: str) -> BaseResumeParser:
        import os
        _, ext = os.path.splitext(file_name.lower())
        
        parser_cls = cls._extension_map.get(ext)
        if not parser_cls:
            raise ValueError(f"Extension {ext} is not supported")
            
        return parser_cls()