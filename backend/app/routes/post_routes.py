# this file is backend/app/routes/post_routes.py
from fastapi import APIRouter, HTTPException, Query
from app.config import db
router = APIRouter()

# helper to convert MongoDB ObjectId to string
def incident_extractor(cyber_incident) -> dict:
    return {
        "id": str(cyber_incident["_id"]),
        "event_date": str(cyber_incident["event_date"]),
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

# 1. Read the top 9 rows of data from MongoDB
@router.get("/list_incidents", response_description="List all cyber incidents from MongoDB")
async def list_incidents():

    # we put the name of the database.name of collection here!
    posts = await db.europec_maryland_test.find().to_list(3)
    return {"status":201, "result":[incident_extractor(post) for post in posts] }

# 2. Aggregates cyber incidents by industry and month, and also provides a total count of incidents for all industries per month.
@router.get("/aggregate_by_industry_and_month", response_description="Aggregate cyber incidents by industry and month, including total incidents per month.")
async def aggregate_by_industry_and_month():
  
    try:
        pipeline = [
            # Stage 1: Add new fields for year and month.
            {
                "$addFields": {
                    "event_date_dt": {
                        "$dateFromString": {
                            "dateString": "$event_date"
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "year": {"$year": "$event_date_dt"},
                    "month": {"$month": "$event_date_dt"}
                }
            },
            # Stage 2: Use $facet to run multiple aggregations in parallel.
            {
                "$facet": {
                    # Sub-pipeline 1: Group by industry and year,month
                    "by_industry": [
                        {
                            "$group": {
                                "_id": {
                                    "industry": "$affected_industry",
                                    "year": "$year",
                                    "month": "$month"
                                },
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0, # Exclude the _id field
                                "industry": "$_id.industry",
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "count": "$count"
                            }
                        },
                        {
                            "$sort": {
                                "year": 1,
                                "month": 1,
                                "industry": 1
                            }
                        }
                    ],
                    # Sub-pipeline 2: Get total count for all industries by year,month
                    "totals_by_group": [
                        {
                            "$group": {
                                "_id": {
                                    "year": "$year",
                                    "month": "$month"
                                },
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "industry": "All Industries",
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "count": "$count"
                            }
                        },
                        {
                            "$sort": {
                                "year": 1,
                                "month": 1
                            }
                        }
                    ]
                }
            }
        ]

        cursor = db.europec_maryland_test.aggregate(pipeline)
        result = await cursor.to_list(None)

        # The result of $facet is a single document in an array. We return the document itself.
        if result:
            return {"status": 201, "result": result[0]}
        else:
            return {"status": 201, "result": {"by_industry": [], "totals_by_month": []}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 3. Aggregates cyber incidents by industry, and count by the event_subtype.
@router.get("/aggregate_by_industry", response_description="Aggregate cyber incidents by industry and another field.")
async def aggregate_by_industry(
    group_by_field: str = Query("event_subtype", enum=["event_subtype", "affected_country", "motive"])
):
    try:
        pipeline = [
            {
                "$facet": {
                    "by_industry": [
                        {
                            "$group": {
                                "_id": {
                                    "industry": "$affected_industry",
                                    group_by_field: f"${group_by_field}"
                                },
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "industry": "$_id.industry",
                                group_by_field: f"$_id.{group_by_field}",
                                "count": "$count"
                            }
                        },
                        {
                            "$sort": {
                                "industry": 1,
                                "count": -1
                            }
                        }
                    ],
                    "totals_by_group": [
                        {
                            "$group": {
                                "_id": f"${group_by_field}",
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "industry": "All Industries",
                                group_by_field: "$_id",
                                "count": "$count"
                            }
                        },
                        {
                            "$sort": {
                                "count": -1
                            }
                        }
                    ]
                }
            }
        ]

        cursor = db.europec_maryland_test.aggregate(pipeline)
        result = await cursor.to_list(None)

        if result:
            return {"status": 201, "result": result[0]}
        else:
            return {"status": 201, "result": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 4. Aggregates cyber incidents by industry, and count by the actor type & have an extra field actor_type.
@router.get("/aggregate_by_industry_and_actors", response_description="Aggregate cyber incidents by industry and actors.")
async def aggregate_by_industry_AND_actors():
    try:
        pipeline = [
            {
                "$facet": {
                    "by_industry": [
                        {
                            "$group": {
                                "_id": {
                                    "industry": "$affected_industry",
                                    "actor": "$actor",
                                    "actor_type": "$actor_type"
                                },
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "industry": "$_id.industry",
                                "actor": "$_id.actor",
                                "actor_type": "$_id.actor_type",
                                "count": "$count"
                            }
                        },
                        {
                            "$sort": {
                                "industry": 1,
                                "count": -1
                            }
                        }
                    ],
                    "totals_by_group": [
                        {
                            "$group": {
                                "_id": {
                                    "actor": "$actor",
                                    "actor_type": "$actor_type"
                                },
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "industry": "All Industries",
                                "actor": "$_id.actor",
                                "actor_type": "$_id.actor_type",
                                "count": "$count"
                            }
                        },
                        {
                            "$sort": {
                                "count": -1
                            }
                        }
                    ]
                }
            }
        ]

        cursor = db.europec_maryland_test.aggregate(pipeline)
        result = await cursor.to_list(None)

        if result:
            return {"status": 201, "result": result[0]}
        else:
            return {"status": 201, "result": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

