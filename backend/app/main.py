# this file is backend/app/main.py
'''
This is your application’s entry point. It creates the FastAPI app, 
configures middleware (like CORS), and attaches routers that define endpoints to be used by the frontend.
'''
from fastapi import FastAPI
from app.routes.post_routes import router as post_router
from app.routes.post_routes_Marshdata import router as Marsh_post_router
from app.routes.query_routes import router as query_router
from app.routes.ppt_routes import router as ppt_router
from app.routes.data_upload_routes import router as data_upload_router
from app.config.settings import init_mongo, init_tracing
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
if os.getenv("ENVIRONMENT", "DEV") == "DEV":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Specific origin, not *
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

# add posts router
# REQUEST URL ->  http://127.0.0.1:8000/api/list_incidents
app.include_router(query_router, prefix="/api")
app.include_router(ppt_router, prefix="/api")

app.include_router(data_upload_router, prefix="/api", tags=["upload_prop_data"])

# Internet Data Related Pulls
app.include_router(post_router, prefix="/api", tags=["incidents"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry_and_month"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry?group_by_field=event_subtype"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry?group_by_field=affected_country"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry?group_by_field=motive"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry_and_actors"])
app.include_router(post_router, prefix="/api", tags=["Internet_Data"])

# Marsh Data Related Pulls
app.include_router(Marsh_post_router, prefix="/api", tags=["unique_valueFOR"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregate_by_filters"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregateby_Claim_Coverage"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregateby_Loss_Estimate"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregateby_CauseOrType"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregateby_AffectedCountries"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregateby_Claim_Sankey"])
app.include_router(Marsh_post_router, prefix="/api", tags=["aggregateby_IndivIncidents"])
app.include_router(Marsh_post_router, prefix="/api", tags=["Marsh_Data"])

@app.on_event("startup")
async def startup_event():
    init_tracing()
    await init_mongo()
