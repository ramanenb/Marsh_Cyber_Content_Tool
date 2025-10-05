# this file is backend/app/main.py
'''
This is your application’s entry point. It creates the FastAPI app, 
configures middleware (like CORS), and attaches routers that define endpoints to be used by the frontend.
'''
from fastapi import FastAPI
from app.routes.post_routes import router as post_router
from app.routes.query_routes import router as query_router
from app.routes.ppt_routes import router as ppt_router
from app.routes.data_upload_routes import router as data_upload_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# add posts router
# REQUEST URL ->  http://127.0.0.1:8000/api/list_incidents
app.include_router(post_router, prefix="/api", tags=["incidents"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry_and_month"])

app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry?group_by_field=event_subtype"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry?group_by_field=affected_country"])
app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry?group_by_field=motive"])

app.include_router(post_router, prefix="/api", tags=["aggregate_by_industry_and_actors"])

app.include_router(query_router, prefix="/api")
app.include_router(ppt_router, prefix="/api")

app.include_router(data_upload_router, prefix="/api", tags=["upload_prop_data"])
