# this file is backend/app/models/post.py
'''
Data models to define the structure of your data, choosing only the cols we want,
if the database has other columns, they will be ignored
.
'''

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class incidents(BaseModel):
    _id: Optional[str] = Field(None, alias="_id")
    affected_countries: Optional[str]
    affected_organization: Optional[str]
    affected_industry: Optional[str]
    event_type: Optional[str]
    event_subtype: Optional[str]
    motive: Optional[str]
    description: Optional[str]
    actor: Optional[str]
    actor_type: Optional[str]
    actor_country: Optional[str]

    class Config:
        populate_by_name = True,
        json_schema_extra = {
            "example": {
                "affected_countries": "Singapore",
                "affected_organization": "Oshee B Shee",
                "affected_industry": "Financial Services",
                "event_type": "Ransomeware",
                "event_subtype": "Subtype A",
                "motive": "Financial Gain",
                "description": "Detailed description of the event.",
                "actor": "hackerbois",
                "actor_type": "Individual",
                "actor_country": "Malysia"
            }
        }
