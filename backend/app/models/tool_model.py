from typing import List, Optional
from pydantic import BaseModel

class RetrieverInput(BaseModel):
    query: str
    start_date: str
    end_date: Optional[str] = None
    industries: List[str] = []
    region: Optional[str] = None

class TavilyInput(BaseModel):
    query: str
    start_date: str
    end_date: Optional[str] = None
    industries: List[str] = []
    region: Optional[str] = None