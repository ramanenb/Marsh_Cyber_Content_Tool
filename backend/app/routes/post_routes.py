# this file is backend/app/routes/post_routes.py
from fastapi import APIRouter, HTTPException
from app.config import db
router = APIRouter()

# helper to convert MongoDB ObjectId to string
def incident_extractor(cyber_incident) -> dict:
    return {
        "id": str(cyber_incident["_id"]),
        "affected_country": str(cyber_incident["affected_country"]),
        "affected_organization": str(cyber_incident["affected_organization"]),
        "affected_industry": str(cyber_incident["affected_industry"]),
        "event_type": str(cyber_incident["event_type"]),
        "event_subtype": str(cyber_incident["event_subtype"]),
        "motive": str(cyber_incident["motive"]),
        "description": str(cyber_incident["description"]),
        "actor": str(cyber_incident["actor"]),
        "actor_type": str(cyber_incident["actor_type"]),
        "actor_country": str(cyber_incident["actor_country"])
    }

# Read the top 9 rows of data from MongoDB
@router.get("/list_incidents", response_description="List all cyber incidents from MongoDB")
async def list_incidents():
    # we put the name of the collection here!
    posts = await db.europec_maryland_test.find().to_list(3)
    return {"status":201, "result":[incident_extractor(post) for post in posts] }

