from pydantic import BaseModel
from typing import Optional, List

class IncidentRequest(BaseModel):
    query: str
    industries: List[str]
    region: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class IncidentResponse(BaseModel):
    query: str
    industries: List[str]
    region: Optional[str]
    evaluated_articles: List