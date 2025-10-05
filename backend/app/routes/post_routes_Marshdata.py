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

@router.get("/unique_valueFOR", response_description="Find unique values for cause or claim type col", tags=["find_unqiue_ValueInCol"])
async def find_unique(
    group_by_field: str = Query("Cause", enum=["Cause", "Type of Claim"])
):
    try:
        # MongoDB aggregation to get distinct values
        pipeline = [
            {"$match": {group_by_field: {"$exists": True, "$ne": None}}},
            {"$group": {"_id": f"${group_by_field}"}},
            {"$sort": {"_id": 1}}
        ]

        cursor = DB.marsh_proprietary_data.aggregate(pipeline)
        results = await cursor.to_list(None)

        unique_values = [r["_id"] for r in results if r["_id"]]

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
        
        all_loss_estimates = []  # For calculating global min/max
        
        for doc in results:
            try:
                value = doc.get("loss_estimate")
                loss_value = float(value)
                
                toc = str(doc.get("type_of_claim", "Unknown"))
                cause = str(doc.get("cause", "Unknown"))
                
                grouped_data[toc][cause].append(loss_value)
                grouped_data[toc]["All Causes"].append(loss_value)
                grouped_data["All Types"][cause].append(loss_value)
                grouped_data["All Types"]["All Causes"].append(loss_value)
                all_loss_estimates.append(loss_value)
                
            except (ValueError, TypeError, AttributeError):
                continue
        
        if not all_loss_estimates:
            return {"status": 200, "message": "No valid loss estimate data found.", "result": {}}

        # 5️. Calculate global min/max for consistent bin ranges across all histograms
        global_min = np.round(min(all_loss_estimates), 0)
        global_max = np.round(max(all_loss_estimates), 0)
        bin_edges = np.round(np.linspace(global_min, global_max, bins + 1),0)
        
        # 6. Create histograms for each Type of Claim and Cause combination
        response = {}
        
        for toc, causes in grouped_data.items():
            response[toc] = {}
            
            for cause, loss_values in causes.items():
                if not loss_values:
                    continue
                
                # Calculate histogram for this specific group
                hist_counts, _ = np.histogram(loss_values, bins=bin_edges)
                
                # Format bin labels
                bin_labels = []
                for i in range(len(bin_edges) - 1):
                    start_label = round(bin_edges[i]/1000,0)
                    end_label = round(bin_edges[i + 1]/1000,0)
                    bin_labels.append(f"{start_label}K-{end_label}K")
                
                # Store histogram data for this group
                response[toc][cause] = {
                    "labels": bin_labels,
                    "datasets": {
                        "data": hist_counts.tolist()
                        # "bin_edges": bin_edges.tolist(),
                        # "total_records": len(loss_values),
                        # "min": float(min(loss_values)),
                        # "max": float(max(loss_values)),
                        # "mean": float(np.mean(loss_values)),
                        # "median": float(np.median(loss_values))
                    }
                }
        
        # # 7️⃣ Add global statistics
        # global_stats = {
        #     "total_records": len(all_loss_estimates),
        #     "min": global_min,
        #     "max": global_max,
        #     "mean": float(np.mean(all_loss_estimates)),
        #     "median": float(np.median(all_loss_estimates)),
        #     "unique_types": len(response)
        # }

        return {
            "status": 200,
            "filters": {"industry": industry, "period": period, "bins": bins},
            "result": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

