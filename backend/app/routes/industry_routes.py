# backend/app/routes/industry_routes.py
from fastapi import APIRouter, HTTPException
from app.config import db

router = APIRouter()


@router.get("/getIndustries")
async def get_industries():
    try:
        industries_collection = db["industries"]
        cursor = industries_collection.find({}, {"_id": 0, "industry": 1})
        industries = [doc["industry"] async for doc in cursor]
        return {"industries": sorted(industries)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
