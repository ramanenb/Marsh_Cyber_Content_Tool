# this file is backend/app/routes/post_routes.py
from collections import defaultdict
import numpy as np
from fastapi import APIRouter, HTTPException, Query
from app.config.settings import DB
from datetime import datetime, timezone
from itertools import pairwise
from bson import ObjectId
router = APIRouter()
from dateutil.relativedelta import relativedelta
import random
import math
import json
from fastapi.responses import JSONResponse

def money_format_value(val):
    if val >= 1_000_000:
        return f"{val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"{int(val/1_000)}K"
    else:
        return f"{int(val)}"
    
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

@router.get("/Marsh_Data", response_description="Find latest Marsh Data Claim Date")
async def get_marsh_data_update():
    doc = await DB.marsh_proprietary_data.find_one({}, sort=[("Incident Date", -1)])
    return {"result" : doc.get("Incident Date")} if doc else None

@router.get("/unique_valueFOR", response_description="Find unique values for cause or claim type col")
async def find_unique(
    group_by_field: str = Query("Cause", enum=["Cause", "Type of Claim"]),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year"),
    industry: str = Query(default="All Industries")
):
    try:
        start_date = process_date(period)

        # MongoDB aggregation to get distinct values
        pipeline = [
            {"$match": {
                "$and": [
                    {group_by_field: {"$exists": True, "$ne": None}},
                    {"Incident Date": {"$gte": start_date}},
                    {} if industry == "All Industries" else {"Industry": industry},
                    ]
                }
            },
            {"$group": {"_id": f"${group_by_field}"}},
            {"$sort": {"_id": 1}}
        ]

        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(None)

        # Clean any NaN or non-JSON values since w/o this it throws an error
        unique_values = []
        for r in results:
            val = r.get("_id")
            # Handle None, NaN, or empty strings
            if val is None or (isinstance(val, float) and math.isnan(val)) or val == "":
                val = "Unknown"
            val = val.replace("FINPRO - ", "")
            unique_values.append(val)

        return {
            "status": 200,
            "field": group_by_field,
            "count": len(unique_values),
            "result": unique_values
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/aggregate_by_filters", response_description="Aggregate incidents by filters")
async def aggregate_by_filters(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year"),
    isChange: int = Query(default= 0)
):
    try:
        start_date = process_date(period)

        # 2️⃣ Build MongoDB pipeline
        pipeline = [
            # Convert Incident Date to Date object
            {
                "$addFields": {
                    "Incident Date_dt": {
                        "$cond": [
                            {"$eq": [{"$type": "$Incident Date"}, "string"]},
                            {"$dateFromString": {"dateString": "$Incident Date"}},
                            "$Incident Date"
                        ]
                    }
                }
            },
            # Filter by selected industry (if not "All Industries") and date range
            {
                "$match": {
                    "$and": [
                        {"Incident Date": {"$gte": start_date}},
                        {} if industry == "All Industries" else {"Industry": industry}
                    ]
                }
            },
            # Extract year & month for grouping
            {
                "$addFields": {
                    "year": {"$year": "$Incident Date_dt"},
                    "month": {"$month": "$Incident Date_dt"}
                }
            },
            # Group by Type of Claim, Cause, Year, and Month
            {
                "$group": {
                    "_id": {
                        "type_of_claim": "$Type of Claim",
                        "cause": "$Cause",
                        "year": "$year",
                        "month": "$month"
                    },
                    "count": {"$sum": 1}
                }
            },
            # Format output
            {
                "$project": {
                    "_id": 0,
                    "type_of_claim": "$_id.type_of_claim",
                    "cause": "$_id.cause",
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "count": 1
                }
            },
            {"$sort": {"year": 1, "month": 1}}
        ]

        # 3️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(None)

        if not results:
            return {"status": 200, "message": "No data found for selected filters.", "result": []}

        # 4️⃣ Post-process results into frontend format
        grouped_data = defaultdict(lambda: defaultdict(lambda: {"labels": [], "data": []}))
        # structure: grouped_data[type_of_claim][cause] = {"labels": [], "data": []}

        for doc in results:
            toc = doc.get("type_of_claim") or "Unknown"
            toc = str(toc)
            toc = toc.replace("FINPRO - ", "")
            cause = doc.get("cause") or "Unknown"
            label = f"{doc['month']}-{str(doc['year'])[-2:]}"
            grouped_data[toc][cause]["labels"].append(label)
            grouped_data[toc][cause]["data"].append(doc["count"])

        # add in data for ALL Causes for each Type of Claim
        for toc, causes in grouped_data.items():
            all_cause_totals = defaultdict(int)
            
            for cause, values in causes.items():
                labels_list = values["labels"]
                data_list = values["data"]
                for label, count in zip(labels_list, data_list):
                    all_cause_totals[label] += count  
            
            # sort keys
            sorted_keys = sorted(all_cause_totals.keys(), key=lambda k: (k[-2:], k[:-3]))
            sorted_dict = {key: all_cause_totals[key] for key in sorted_keys}
            
            grouped_data[toc]["All Causes"] = {
                "labels": list(sorted_dict.keys()),
                "data": list(sorted_dict.values())
            }
        
        # Repeat the above 2 BUT for ALL CLAIM TYPES
        all_types_data  = defaultdict(lambda: defaultdict(int))
        for toc, causes in grouped_data.items():
            for cause, values in causes.items():
                for label, count in zip(values["labels"], values["data"]):
                    all_types_data[cause][label] += count

        # Step 4: Build into grouped_data["All Types"]
        for cause, label_counts in all_types_data.items():
            sorted_keys = sorted(label_counts.keys(), key=lambda k: (k[-2:], k[:-3]))
            sorted_dict = {key: label_counts[key] for key in sorted_keys}
            grouped_data["All Types"][cause] = {
                "labels": list(sorted_dict.keys()),
                "data": list(sorted_dict.values())
            }
        
        # Step 5. for the Change over Time, simply remove the first month and find Period2Period to Change
        edited_data = defaultdict(lambda: defaultdict(lambda: {"labels": [], "data": []}))
        if isChange:
            for toc, causes in grouped_data.items():
                for cause, values in causes.items():
                    labels_list = values["labels"]
                    data_list = values["data"]
                    if len(labels_list) > 1:
                        labels_list = labels_list[1:]
                        data_list = [b - a for a,b in zip(data_list[:-1], data_list[1:])]

                    else:
                        labels_list = [""]
                        data_list = [0]

                    for label, count in zip(labels_list, data_list):
                        edited_data[toc][cause]["labels"].append(label)
                        edited_data[toc][cause]["data"].append(count)
            
        # Final response structure
        response = {
            toc: {
                cause: {
                    "labels": val["labels"],
                    "datasets": {"label": cause, "data": val["data"]}
                }
                for cause, val in causes.items()
            }
            for toc, causes in (grouped_data.items() if isChange == 0 else edited_data.items())
        }

        return {
            "status": 200,
            "filters": {"industry": industry, "period": period},
            "result": response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Aggregates cyber incident coverage of claims
@router.get("/aggregateby_Claim_Coverage", response_description="Aggregate cyber incidents by industry and another field.")
async def aggregate_by_Coverage(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year")
):
    try:
        start_date = process_date(period)

        # 2️⃣ Build MongoDB pipeline
        pipeline = [
            # Filter by selected industry (if not "All Industries") and date range
                { "$match": {
                    "$and": [
                        {"Incident Date": {"$gte": start_date}},
                        {} if industry == "All Industries" else {"Industry": industry}
                    ]
                }},
                # Group by Type of Claim, Cause, Coverage
                { "$group": {
                        "_id": {
                            "type_of_claim": "$Type of Claim",
                            "cause": "$Cause",
                            "coverage": "$Coverage"
                        },
                        "count": {"$sum": 1}
                }},
                # Format output
                { "$project": {
                        "_id": 0,
                        "type_of_claim": "$_id.type_of_claim",
                        "cause": "$_id.cause",
                        "Coverage": "$_id.coverage",
                        "count": 1
                }},
                {"$sort": {"count": -1}}
        ]

        # 3️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(None)

        if not results:
            return {"status": 200, "message": "No data found for selected filters.", "result": []}

        # 4️⃣ Post-process results into frontend format
        grouped_data = defaultdict(lambda: defaultdict(lambda: {"labels": [], "data": []}))
        # structure: grouped_data[type_of_claim][cause] = {"labels": [], "data": []}

        for doc in results:
            toc = doc.get("type_of_claim") or "Unknown"
            cause = doc.get("cause") or "Unknown"
            label = doc.get("Coverage") or "Unknown"

            toc = str(toc)
            toc = toc.replace("FINPRO - ", "")
            cause = str(cause)
            label = str(label)

            grouped_data[toc][cause]["labels"].append(label)
            grouped_data[toc][cause]["data"].append(doc["count"])

        # add in data for ALL Causes for each Type of Claim
        for toc, causes in grouped_data.items():
            all_cause_totals = defaultdict(int)
            
            for cause, values in causes.items():
                labels_list = values["labels"]
                data_list = values["data"]
                for label, count in zip(labels_list, data_list):
                    all_cause_totals[label] += count  
            
            # sort keys
            sorted_keys = sorted(all_cause_totals.items(), key= lambda item: item[1], reverse=True)
            sorted_dict = dict(sorted_keys)
            
            grouped_data[toc]["All Causes"] = {
                "labels": list(sorted_dict.keys()),
                "data": list(sorted_dict.values())
            }
        
        # Repeat the above 2 BUT for ALL CLAIM TYPES
        all_types_data  = defaultdict(lambda: defaultdict(int))
        for toc, causes in grouped_data.items():
            for cause, values in causes.items():
                for label, count in zip(values["labels"], values["data"]):
                    all_types_data[cause][label] += count

        # Step 4: Build into grouped_data["All Types"]
        for cause, label_counts in all_types_data.items():
            sorted_keys = sorted(label_counts.items(), key= lambda item: item[1], reverse=True)
            sorted_dict = dict(sorted_keys)
            grouped_data["All Types"][cause] = {
                "labels": list(sorted_dict.keys()),
                "data": list(sorted_dict.values())
            }
            
        # Final response structure
        response = {
            toc: {
                cause: {
                    "labels": val["labels"],
                    "datasets": {"label": cause, "data": val["data"]}
                }
                for cause, val in causes.items()
            }
            for toc, causes in grouped_data.items()
        }

        return {
            "status": 200,
            "filters": {"industry": industry, "period": period},
            "result": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Generate Loss Estimate Histogram
@router.get("/aggregateby_Loss_Estimate", response_description="Aggregate cyber incidents by Loss Estimate")
async def aggregate_by_Loss_Estimate(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year"),
    bins: int = Query(default=10, description="Number of histogram bins")
):
    try:
        start_date = process_date(period)

        # 2️⃣ Build MongoDB pipeline to extract Loss Estimate with Type of Claim and Cause
        pipeline = [
            # Filter by date range and industry
            {
                "$match": {
                    "Incident Date": {"$gte": start_date},
                    **({"Industry": industry} if industry != "All Industries" else {}),
                    "Marsh Loss Estimate (USD)": {"$exists": True, "$ne": None}
                }
            },
            # Project necessary fields
            {
                "$project": {
                    "_id": 0,
                    "loss_estimate": "$Marsh Loss Estimate (USD)",
                    "type_of_claim": {"$ifNull": ["$Type of Claim", "Unknown"]},
                    "cause": {"$ifNull": ["$Cause", "Unknown"]}
                }
            }
        ]

        # 3️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(None)

        if not results:
            return {"status": 200, "message": "No data found for selected filters.", "result": {}}
        
        # 4️⃣ Group data by Type of Claim and Cause
        from collections import defaultdict
        import numpy as np
        
        grouped_data = defaultdict(lambda: defaultdict(list))
        # Structure: grouped_data[type_of_claim][cause] = [loss_estimate1, loss_estimate2, ...]
        
        for doc in results:
            try:
                value = doc.get("loss_estimate")
                loss_value = float(value)
                
                toc = str(doc.get("type_of_claim", "Unknown"))
                toc = toc.replace("FINPRO - ", "")
                cause = str(doc.get("cause", "Unknown"))
                
                grouped_data[toc][cause].append(loss_value)
                grouped_data[toc]["All Causes"].append(loss_value)
                grouped_data["All Types"][cause].append(loss_value)
                grouped_data["All Types"]["All Causes"].append(loss_value)
                
            except (ValueError, TypeError, AttributeError):
                continue
        
        # 5. Create histograms for each Type of Claim and Cause combination
        response = {}
        
        for toc, causes in grouped_data.items():
            response[toc] = {}
            
            for cause, loss_values in causes.items():
                if not loss_values:
                    continue

                # 6. Calculate local min/max for each histogram
                local_min = np.round(min(loss_values), 0)
                local_max = np.round(max(loss_values), 0)
                bin_edges = np.round(np.linspace(local_min, local_max, bins + 1),0)
                
                # Calculate histogram for this specific group
                hist_counts, _ = np.histogram(loss_values, bins=bin_edges)
                
                # Format bin labels for start_label to end_label
                bin_labels = []
                bin_labels = [f"{money_format_value(bin_edges[i])}-{money_format_value(bin_edges[i+1])}" 
                    for i in range(len(bin_edges) - 1)]
                
                # Store histogram data for this group
                response[toc][cause] = {
                    "labels": bin_labels,
                    "datasets": {
                        "data": hist_counts.tolist()
                    }
                }

        return {
            "status": 200,
            "filters": {"industry": industry, "period": period, "bins": bins},
            "result": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Generate aggregation by Claim Cause OR Claim Type
@router.get("/aggregateby_CauseOrType", response_description="Aggregate cyber incidents by ClaimType or Cause")
async def aggregate_by_CauseOrType(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year"),
    group_by_field: str = Query(default="Cause", enum=["Cause", "Type of Claim"]),
    aggregation_method: str = Query(default="Count", enum=["Count", "Sum_Loss", "Avg_Loss"])
):
    try:
        start_date = process_date(period)

        # 2️⃣ Determine fields
        if group_by_field == "Cause":
            secondary_field = "Type of Claim"
            all_key = "All Types"
        else:
            secondary_field = "Cause"
            all_key = "All Causes"

        # 3️⃣ Build aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "Incident Date": {"$gte": start_date},
                    **({"Industry": industry} if industry != "All Industries" else {})
                }
            },
            {
                "$facet": {
                    # Group by secondary field first, then group_by_field. Grouping is done in 2 stages as
                    ## { _id: {Cause: "Fire", Type: "Manufacturing"}, count: 50 }
                    ## { _id: {Cause: "Fire", Type: "Retail"}, count: 30 }
                    ## TO nested form
                    ## {
                    ## "_id": "Fire",
                    ## "sub_groups": [
                    ##     {"Type": "Manufacturing", "count": 50},
                    ##     {"Type": "Retail", "count": 30}
                    ## ],
                    ## "total": 80
                    ## }

                    "grouped": [
                        {
                            "$group": {
                                "_id": {
                                    secondary_field: f"${secondary_field}",
                                    group_by_field: f"${group_by_field}"
                                },
                                "count": (
                                    {"$sum": "$Marsh Loss Estimate (USD)"} if aggregation_method == "Sum_Loss" else 
                                    {"$avg": "$Marsh Loss Estimate (USD)"} if aggregation_method == "Avg_Loss" else 
                                    {"$sum": 1}
                                )
                            }
                        },
                        {
                            "$group": {
                                "_id": f"$_id.{secondary_field}",
                                "sub_groups": {
                                    "$push": {
                                        group_by_field: f"$_id.{group_by_field}",
                                        "count": "$count"
                                    }
                                },
                                "total": {"$sum": "$count"}
                            }
                        },
                        {"$sort": {"total": -1}}
                    ],
                    # Overall totals (All Causes / All Types)
                    all_key: [
                        {
                            "$group": {
                                "_id": f"${group_by_field}",
                                "count": (
                                    {"$sum": "$Marsh Loss Estimate (USD)"} if aggregation_method == "Sum_Loss" else 
                                    {"$avg": "$Marsh Loss Estimate (USD)"} if aggregation_method == "Avg_Loss" else 
                                    {"$sum": 1}
                                )
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                group_by_field: "$_id",
                                "count": 1
                            }
                        },
                        {"$sort": {"count": -1}}
                    ]
                }
            }
        ]

        # 4️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        agg_results = await cursor.to_list(None)
        if not agg_results or not agg_results[0]:
            return {"status": 200, "result": {"Output": {}}}

        result = agg_results[0]

        # 5️⃣ Format response
        response = {"Output": {}}

        # (a) Add grouped data by secondary_field
        grouped_output = {}
        for entry in result["grouped"]:
            sec_label = entry["_id"].replace("FINPRO - ", "")
            labels = [x[group_by_field].replace("FINPRO - ", "") for x in entry["sub_groups"]]
            data = [round(
                    (0.001 if aggregation_method in ["Sum_Loss", "Avg_Loss"] else 1.0) *
                    x["count"],1) for x in entry["sub_groups"] ]

            grouped_output[sec_label] = {
                "labels": labels,
                "datasets": {
                    "label": group_by_field,
                    "data": data
                }
            }

        # (b) Add overall totals
        all_labels = [doc[group_by_field].replace("FINPRO - ", "") for doc in result[all_key]]
        all_data = [round(
                (0.001 if aggregation_method in ["Sum_Loss", "Avg_Loss"] else 1.0) *
                doc["count"],1) for doc in result[all_key]]
        
        grouped_output[all_key] = {
            "labels": all_labels,
            "datasets": {
                "label": group_by_field,
                "data": all_data
            }
        }

        response["Output"] = grouped_output

        return {"status": 201, "result": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. Aggregate by Affected Countries
@router.get("/aggregateby_AffectedCountries", response_description="Aggregate cyber incidents by Affected Industries.")
async def aggregate_by_AffectedCountries(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' for 3 months, '1Y' for 1 year")
):
    try:
        start_date = process_date(period)

        # 2️⃣ Build MongoDB pipeline
        pipeline = [
            # Filter by selected industry (if not "All Industries") and date range
                { "$match": {
                    "$and": [
                        {"Incident Date": {"$gte": start_date}},
                        {} if industry == "All Industries" else {"Industry": industry}
                    ]
                }},
                # Group by Type of Claim, Cause, Affected Countries
                { "$group": {
                        "_id": {
                            "type_of_claim": "$Type of Claim",
                            "cause": "$Cause",
                            "coverage": "$Country (Set ID)"
                        },
                        "count": {"$sum": 1}
                }},
                # Format output
                { "$project": {
                        "_id": 0,
                        "type_of_claim": "$_id.type_of_claim",
                        "cause": "$_id.cause",
                        "Affected_Country": "$_id.coverage",
                        "count": 1
                }},
                {"$sort": {"count": -1}}
        ]

        # 3️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(None)

        if not results:
            return {"status": 200, "message": "No data found for selected filters.", "result": []}

        # 4️⃣ Post-process results into frontend format
        grouped_data = defaultdict(lambda: defaultdict(lambda: {"labels": [], "data": []}))
        # structure: grouped_data[type_of_claim][cause] = {"labels": [], "data": []}

        for doc in results:
            toc = doc.get("type_of_claim") or "Unknown"
            cause = doc.get("cause") or "Unknown"
            label = doc.get("Affected_Country") or "Unknown"

            toc = str(toc)
            toc = toc.replace("FINPRO - ", "")
            cause = str(cause)
            label = str(label)

            grouped_data[toc][cause]["labels"].append(label)
            grouped_data[toc][cause]["data"].append(doc["count"])

        # add in data for ALL Causes for each Type of Claim
        for toc, causes in grouped_data.items():
            all_cause_totals = defaultdict(int)
            
            for cause, values in causes.items():
                labels_list = values["labels"]
                data_list = values["data"]
                for label, count in zip(labels_list, data_list):
                    all_cause_totals[label] += count  
            
            # sort keys
            sorted_keys = sorted(all_cause_totals.items(), key= lambda item: item[1], reverse=True)
            sorted_dict = dict(sorted_keys)
            
            grouped_data[toc]["All Causes"] = {
                "labels": list(sorted_dict.keys()),
                "data": list(sorted_dict.values())
            }
        
        # Repeat the above 2 BUT for ALL CLAIM TYPES
        all_types_data  = defaultdict(lambda: defaultdict(int))
        for toc, causes in grouped_data.items():
            for cause, values in causes.items():
                for label, count in zip(values["labels"], values["data"]):
                    all_types_data[cause][label] += count

        # Step 4: Build into grouped_data["All Types"]
        for cause, label_counts in all_types_data.items():
            sorted_keys = sorted(label_counts.items(), key= lambda item: item[1], reverse=True)
            sorted_dict = dict(sorted_keys)
            grouped_data["All Types"][cause] = {
                "labels": list(sorted_dict.keys()),
                "data": list(sorted_dict.values())
            }
        
        # Final response structure - ONLY THING that had to be changed compared to the Claim_Coverage ONE
        response = {
            toc: {
                cause: {
                    "labels": ["Countries"],
                    "datasets": [
                        {"label": x, 
                         "data": [y], 
                         "backgroundColor": random.choice(["#1E3A8A", "#60A5FA", "#1D8494", "#111F30", "#6366F1"])
                        } for x,y in zip(val["labels"], val["data"])
                    ]
                }
                for cause, val in causes.items()
            }
            for toc, causes in grouped_data.items()
        }

        return {
            "status": 200,
            "filters": {"industry": industry, "period": period},
            "result": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 7. Aggregates cyber incident for Sankey Chart showing claim type & result
@router.get("/aggregateby_Claim_Sankey", response_description="Aggregate cyber incidents by Type of Claim & Result of Claim.")
async def aggregate_by_Sankey(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' or '1Y'")
):
    try:
        start_date = process_date(period)

        # 2️⃣ MongoDB pipeline
        pipeline = [
            {
                "$match": {
                    "$and": [
                        {"Incident Date": {"$gte": start_date}},
                        {} if industry == "All Industries" else {"Industry": industry}
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "type_of_claim": "$Type of Claim",
                        "cause": "$Cause",
                        "claim_result": "$Claim Result"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "type_of_claim": "$_id.type_of_claim",
                    "cause": "$_id.cause",
                    "from": "$_id.type_of_claim",
                    "to": "$_id.claim_result",
                    "count": 1
                }
            },
            {"$sort": {"count": -1}}
        ]

        # 3️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        if not results:
            return JSONResponse(
                content={"status": 200, "message": "No data found for selected filters.", "result": []},
                media_type="application/json"
            )

        grouped_data = {}

        for doc in results:
            toc = str(doc.get("type_of_claim") or "Unknown")
            toc = toc.replace("FINPRO - ", "")
            cause = str(doc.get("cause") or "Unknown")
            from_label = str(doc.get("from") or "Unknown")
            from_label = from_label.replace("FINPRO - ", "")
            to_label = str(doc.get("to") or "Unknown")
            count = doc.get("count", 0)

            # Sanitize count
            if not isinstance(count, (int, float)) or math.isnan(count) or math.isinf(count):
                count = 0

            # Initialize nested dicts
            grouped_data.setdefault(toc, {})
            grouped_data[toc].setdefault(cause, {"links": []})

            grouped_data[toc][cause]["links"].append([
                from_label,
                to_label,
                int(count)
            ])

        # 5️⃣ Add "All Causes" per Type of Claim
        for toc, causes in grouped_data.items():
            all_links = defaultdict(int)
            for cause, values in causes.items():
                for f, t, w in values["links"]:
                    all_links[(f, t)] += w  # Use tuple key

            grouped_data[toc]["All Causes"] = {
                "links": [[f, t, w] for (f, t), w in all_links.items()]
            }

        # 6️⃣ Add "All Types"
        all_types = defaultdict(lambda: defaultdict(int))
        for toc, causes in grouped_data.items():
            for cause, values in causes.items():
                for f, t, w in values["links"]:
                    all_types[cause][(f, t)] += w  # Use tuple key

        for cause, pairs in all_types.items():
            grouped_data.setdefault("All Types", {})
            grouped_data["All Types"][cause] = {
                "links": [[f, t, w] for (f, t), w in pairs.items()]
            }

        # Build plain response dict
        response = {}
        for toc, causes in grouped_data.items():
            response[toc] = {}
            for cause, val in causes.items():
                response[toc][cause] = {"data": val["links"]}

        return JSONResponse(
            content={
                "status": 200,
                "filters": {"industry": industry, "period": period},
                "result": response
            },
            media_type="application/json"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

def sanitize_for_json(obj):
    """
    Recursively convert NaN, inf, -inf into None for safe JSON serialization.
    Works for dicts, lists, and scalars.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj

# 8. Aggregates cyber incident for Sankey Chart showing claim type & result
@router.get("/aggregateby_IndivIncidents", response_description="Extract all the relevant incidents for that particular filter.")
async def aggregate_by_ClaimIncidents(
    industry: str = Query(default="All Industries"),
    period: str = Query(default="1Y", description="Time period: e.g. '3M' or '1Y'"),
    Cause: str = Query(default = "All Causes", description = "What causes this cyber incident"),
    ClaimType: str = Query(default = "All Types", description = "What claim type was used")
):
    try:
        start_date = process_date(period)

        # Build the match conditions
        match_conditions = [
            {"Incident Date": {"$gte": start_date}},
            {} if industry == "All Industries" else {"Industry": industry},
            {} if Cause == "All Causes" else {"Cause": Cause}
        ]

        if ClaimType != "All Types":
            # Match after removing "FINPRO -" prefix from the database field
            match_conditions.append({
                "$expr": {
                    "$eq": [
                        {
                            "$trim": {
                                "input": {
                                    "$replaceAll": {
                                        "input": "$Type of Claim",
                                        "find": "FINPRO -",
                                        "replacement": ""
                                    }
                                }
                            }
                        },
                        ClaimType
                    ]
                }
            })

        # 2️⃣ MongoDB pipeline
        pipeline = [
            {
                "$match": {
                    "$and": match_conditions
                }
            },
            { "$sort": { "Incident Date": -1 } },
            { "$limit": 40 },
            {
                "$project": {
                    "_id": 0,
                    "Client": "$Client Name",
                    "Industry": "$Industry",
                    "Incident_Date": {
                        "$cond": [
                            { "$eq": [ { "$type": "$Incident Date" }, "missing" ] },
                            None,
                            { "$dateToString": { "format": "%Y-%m-%d", "date": "$Incident Date" } }
                        ]
                    },
                    "Cause": "$Cause",
                    "Claim_Type": {
                        "$trim": {
                            "input": {
                                "$replaceAll": {
                                    "input": "$Type of Claim",
                                    "find": "FINPRO -",
                                    "replacement": ""
                                }
                            }
                        }
                    },
                    "Claim_SubType": "$Sub Type of Claim",
                    "Marsh_Loss_Estimate_USD": { "$ifNull": ["$Marsh Loss Estimate (USD)", 0] },
                    "Total_Paid_USD": { "$ifNull": ["$Total Paid (USD)", 0] },
                    "Description": "$Brief Description of Incident",
                    "Loss_Details": "$Loss Details",
                    "Claim_Result": "$Claim Result",
                    "Claim_Pos": "$Claim Position",
                    "Total_Paid": { "$ifNull": ["$Total Paid", 0] },
                    "Policy_Currency": "$Policy Currency"
                }
            }
        ]

        # 3️⃣ Run aggregation
        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        results = sanitize_for_json(results)
        if not results:
            return JSONResponse(
                content={"status": 200, "message": "No data found for selected filters.", "result": []},
                media_type="application/json"
            )

        return JSONResponse(
            content={
                "status": 200,
                "filters": {"industry": industry, "period": period},
                "result": results
            },
            media_type="application/json"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

