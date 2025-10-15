# this file is backend/app/routes/post_routes.py
from collections import defaultdict
from fastapi import APIRouter, HTTPException, Query
from app.config.settings import DB
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from bson import ObjectId
router = APIRouter()

def process_date(period: str):
    # 1️⃣ Parse time period (e.g. '3M', '1Y')
    now = datetime.now(timezone.utc)
    if period.endswith("M"):
        months = int(period[:-1])
        start_date = now - relativedelta(months=months)
    elif period.endswith("Y"):
        years = int(period[:-1])
        start_date = now - relativedelta(years=years)
    else:
        raise HTTPException(status_code=400, detail="Invalid period format. Use '3M' or '1Y'.")
    return start_date

@router.get("/list_incidents", response_description="List latest cyber incidents")
async def get_latest_incidents_by_industry(
    industry: str = Query(..., description="Industry name or 'All Industries'"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year")):
    
    try:
        start_date = process_date(period)

        pipeline = [
            {
                "$match": {
                    "$and": [
                        {"event_date": {"$gte": start_date}},
                        {} if industry == "All Industries" else {"affected_industry": industry}
                    ]
                }
            },
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
            { "$limit": 40 },
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

        cursor = DB.europec_maryland_test.aggregate(pipeline)
        response = await cursor.to_list(None)
        return {"result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Aggregates cyber incidents by industry and month, and also provides a total count of incidents for all industries per month.
@router.get("/aggregate_by_industry_and_month", response_description="Aggregate cyber incidents by industry and month, including total incidents per month.")
async def aggregate_by_industry_and_month(period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year")):
  
    try:
        start_date = process_date(period)

        pipeline = [
            {
                "$match": {"event_date": {"$gte": start_date}}
            },
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

        cursor = DB.europec_maryland_test.aggregate(pipeline)
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
    group_by_field: str = Query("event_subtype", enum=["event_subtype", "affected_country", "motive"]),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year")
):
    try:
        start_date = process_date(period)

        pipeline = [
            {
                "$match": {"event_date": {"$gte": start_date}}
            },
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

        cursor = DB.europec_maryland_test.aggregate(pipeline)
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
async def aggregate_by_industry_AND_actors(period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year")):
    try:
        start_date = process_date(period)

        pipeline = [
            {
                "$match": {"event_date": {"$gte": start_date}}
            },
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

        cursor = DB.europec_maryland_test.aggregate(pipeline)
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

