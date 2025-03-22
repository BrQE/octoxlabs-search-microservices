from functools import lru_cache
from ..services.converter_service import ConverterService

@lru_cache()    
def get_converter_service() -> ConverterService:
    return ConverterService()