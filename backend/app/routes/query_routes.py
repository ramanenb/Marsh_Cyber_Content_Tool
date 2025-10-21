from fastapi import APIRouter, HTTPException
from app.models.query_model import IncidentRequest, IncidentResponse
from app.services.query_service import get_industry_list
from app.services.graph_service import run_graph

router = APIRouter()

@router.get("/getIndustries")
async def get_industries():
    try:
        industries = await get_industry_list()
        return {"industries": sorted(industries)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/getIncidents", response_model=IncidentResponse)
async def get_incidents(request: IncidentRequest):
    try:
        print("DEBUG request:", request)
        return await run_graph(request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
