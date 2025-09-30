# this file is backend/app/routes/post_routes.py
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Query
from app.config import db
from datetime import datetime
from bson import ObjectId
router = APIRouter()

# 1. Read the top 9 rows of data from MongoDB
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

router = APIRouter()

@router.get("/list_incidents", response_description="List latest cyber incidents")
async def get_latest_incidents_by_industry(industry: str = Query(..., description="Industry name or 'All Industries'")):
    try:
        if industry == "All Industries":
            # Fetch latest 30 incidents across all industries
            pipeline = [
                {
                    "$addFields": {
                        "event_date_dt": {
                            "$cond": [
                                { "$eq": [ { "$type": "$event_date" }, "string" ] },
                                { "$dateFromString": { "dateString": "$event_date" } },
                                "$event_date"
                            ]
                        }
                    }
                },
                { "$sort": { "event_date_dt": -1 } },
                { "$limit": 30 },
                {
                    "$project": {
                        "_id": 0,
                        "id": { "$toString": "$_id" },
                        "Event_date": {
                            "$cond": [
                                { "$eq": [ { "$type": "$event_date_dt" }, "missing" ] },
                                None,
                                { "$dateToString": { "format": "%Y-%m-%d", "date": "$event_date_dt" } }
                            ]
                        },
                        "Victim_Origin": "$affected_country",
                        "Victim": "$affected_organization",
                        "Industry": "$affected_industry",
                        "event_type": 1,
                        "event_subtype": 1,
                        "Motive": "$motive",
                        "Description": "$description",
                        "Attacker": "$actor",
                        "actor_type": 1,
                        "Attacker_Origin": "$actor_country",
                        "Link": "$source_url"
                    }
                }
            ]
        else:
            # Fetch top 30 recent incidents for the specific industry
            pipeline = [
                { "$match": { "affected_industry": industry } },
                {
                    "$addFields": {
                        "event_date_dt": {
                            "$cond": [
                                { "$eq": [ { "$type": "$event_date" }, "string" ] },
                                { "$dateFromString": { "dateString": "$event_date" } },
                                "$event_date"
                            ]
                        }
                    }
                },
                { "$sort": { "event_date_dt": -1 } },
                { "$limit": 30 },
                {
                    "$project": {
                        "_id": 0,
                        "id": { "$toString": "$_id" },
                        "Event_date": {
                            "$cond": [
                                { "$eq": [ { "$type": "$event_date_dt" }, "missing" ] },
                                None,
                                { "$dateToString": { "format": "%Y-%m-%d", "date": "$event_date_dt" } }
                            ]
                        },
                        "Victim_Origin": "$affected_country",
                        "Victim": "$affected_organization",
                        "Industry": "$affected_industry",
                        "event_type": 1,
                        "event_subtype": 1,
                        "Motive": "$motive",
                        "Description": "$description",
                        "Attacker": "$actor",
                        "actor_type": 1,
                        "Attacker_Origin": "$actor_country",
                        "Link": "$source_url"
                    }
                }
            ]

        cursor = db.europec_maryland_test.aggregate(pipeline)
        response = await cursor.to_list(None)
        return {"result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Aggregates cyber incidents by industry and month, and also provides a total count of incidents for all industries per month.
@router.get("/aggregate_by_industry_and_month", response_description="Aggregate cyber incidents by industry and month, including total incidents per month.")
async def aggregate_by_industry_and_month():
  
    try:
        pipeline = [
            # Stage 1: Add new fields for year and month.
            {
                "$addFields": {
                    "event_date_dt": {
                    "$cond": [
                        { "$eq": [ { "$type": "$event_date" }, "string" ] },
                        { "$dateFromString": { "dateString": "$event_date" } },
                        "$event_date"
                    ]
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
                                "industry": 1,
                                "year": 1,
                                "month": 1
                            }
                        }
                    ]
                }
            }
        ]

        cursor = db.europec_maryland_test.aggregate(pipeline)
        agg_results  = await cursor.to_list(None)

        '''
            The result is in a {"by_industry": {
                "industry": "Accommodation and Food Services",
                "year": 2019,
                "month": 1,
                "count": 5
                },
                {
                "industry": "Accommodation and Food Services",
                "year": 2019,
                "month": 2,
                "count": 6
                },
            } format --> 
            so we need to process this to -->
            {
            sales: {
                labels: ["1-19],
                datasets: { label: "Mobile apps", data: [50, 40, 300, 320, 500, 350, 200, 230, 500] },
            },
            tasks: {
                labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: { label: "Websites", data: [30, 90, 40, 140, 290, 290, 340, 230, 400] },
            },
            }
        '''
        if agg_results:
            industry_data = defaultdict(lambda: {"labels": [], "data": []})

            for i in ["totals_by_group", "by_industry"]:
                for doc in agg_results[0][i]:
                    industry = doc.get("industry")
                    year = doc.get("year")
                    month = doc.get("month")
                    count = doc.get("count")

                    # Basic validation
                    if not industry or not year or not month:
                        continue

                    # Format label (e.g., "1-19")
                    label = f"{month}-{str(year)[-2:]}"
                    industry_data[industry]["labels"].append(label)
                    industry_data[industry]["data"].append(count)
            
            # Build final response
            response = {
                industry: {
                    "labels": values["labels"],
                    "datasets": {
                        "label": industry,
                        "data": values["data"]
                    }
                }
                for industry, values in industry_data.items()
            }

            return {"status": 201, "result": response}

        else:
            return {"status": 201, "result": {"by_industry": ["nil"], "totals_by_month": []}}

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
        agg_results = await cursor.to_list(None)

        if agg_results:
            industry_data = defaultdict(lambda: {"labels": [], "data": []})

            for i in ["totals_by_group", "by_industry"]:
                for doc in agg_results[0][i]:
                    industry = doc.get("industry")
                    group_by = doc.get(group_by_field)
                    count = doc.get("count")

                    industry_data[industry]["labels"].append(group_by)
                    industry_data[industry]["data"].append(count)
            
            # Build final response
            response = {
                industry: {
                    "labels": values["labels"],
                    "datasets": {
                        "label": industry,
                        "data": values["data"]
                    }
                }
                for industry, values in industry_data.items()
            }

            return {"status": 201, "result": response}
        
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
        agg_results = await cursor.to_list(None)

        if agg_results:
            industry_data = defaultdict(lambda: {"labels": [], "data": []})

            for i in ["totals_by_group", "by_industry"]:
                for doc in agg_results[0][i]:
                    industry = doc.get("industry")
                    actor = doc.get("actor")
                    count = doc.get("count")

                    industry_data[industry]["labels"].append(actor)
                    industry_data[industry]["data"].append(count)
            
            # Build final response
            response = {
                industry: {
                    "labels": values["labels"],
                    "datasets": {
                        "label": industry,
                        "data": values["data"]
                    }
                }
                for industry, values in industry_data.items()
            }

            return {"status": 201, "result": response}
        else:
            return {"status": 201, "result": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

