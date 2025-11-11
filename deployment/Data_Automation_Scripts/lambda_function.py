# This script runs in EC2 instance, not as part of FastAPI app. 
# The EC2 should be given IAM role with access to Secrets Manager where MONGO_URL and OPENAI_API_KEY is stored.
# export SECRET_NAME="your_secret_name_in_secrets_manager" in the EC2 environment variables.
import boto3
import os
import json
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
from helper_functions import (download_maryland_data, clean_data, 
                            clean_industries, init_openai_client, build_embedding_text, 
                            get_embedding, country_to_region,
                            INDUSTRY_MAPPING, get_secret) #get_secret

def lambda_handler():
    secret_name = os.environ["SECRET_NAME"]
    secrets = get_secret(secret_name)
    MONGO_URL = secrets["MONGO_URL"]
    mongo_client = MongoClient(MONGO_URL)
    db = mongo_client["DB"]

    # Start date: first day of last month, End date: last day of last month
    today = datetime.date.today()
    first_day_this_month = today.replace(day=1)

    # Move back 1 month
    first_day_two_months_ago = first_day_this_month - relativedelta(months=1)
    last_day_two_months_ago = first_day_this_month - relativedelta(days=1)

    filter_start = first_day_two_months_ago.strftime("%-d/%-m/%Y")
    filter_end = last_day_two_months_ago.strftime("%-d/%-m/%Y")
    print(filter_start)
    print(filter_end)

    # Download data
    file_path = download_maryland_data()
    print("Downloaded")
    df = pd.read_excel(file_path)
    print("Data read Cleaning now")

    # Clean Data
    maryland = clean_data(df, filter_start, filter_end)
    print(f"{len(maryland)} rows")

    # Industries
    print("Industry Mapping")
    maryland["affected_industry"] = maryland["affected_industry"].map(INDUSTRY_MAPPING).fillna(maryland["affected_industry"])
    print("Getting from MONGO")
    industries_collection = db['industries']
    existing = industries_collection.distinct("industry")
    industry_list = list(existing)
    print("Cleaning Industry")
    clean_industries(maryland, industry_list)

    # Embedding 
    print("Building Embedding")
    maryland["event_date"] = pd.to_datetime(df["event_date"])
    maryland['embedding_text'] = maryland.apply(build_embedding_text, axis=1)
    print("Building vectors")
    maryland["vector_embedding"] = maryland["embedding_text"].apply(get_embedding)

    # Region
    print("Region Mapping")
    maryland['Region'] = maryland["affected_country"].apply(country_to_region)

    # Insert
    print("Insert to MongoDB")
    collection = db["europec_maryland_test"]
    records = maryland.to_dict(orient="records")
    if records:
        collection.insert_many(records)
        print(f"Inserted {len(records)} records into MongoDB.")
    else:
        print("No records to insert.")

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} deleted")

    return {
        "status": "success",
        "records_inserted": len(records),
        "filter_start": filter_start,
        "filter_end": filter_end
    }

if __name__ == "__main__":
    result = lambda_handler()
    print(json.dumps(result, indent=4))
