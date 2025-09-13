# this file is backend/app/main.py
'''
This is your application’s entry point. It creates the FastAPI app, 
configures middleware (like CORS), and attaches routers that define endpoints to be used by the frontend.
'''
from fastapi import FastAPI
from app.routes.post_routes import router as post_router
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