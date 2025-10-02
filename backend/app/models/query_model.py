from pydantic import BaseModel
from typing import Optional, List

class IncidentRequest(BaseModel):
    query: str
    industries: List[str]
    region: Optional[str]

class IncidentResponse(BaseModel):
    query: str
    industries: List[str]
    region: Optional[str]
    evaluated_articles: List