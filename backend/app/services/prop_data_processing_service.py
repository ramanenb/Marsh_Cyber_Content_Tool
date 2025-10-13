from app.config.settings import DB, PROPRIETARY_COLLECTION, INDUSTRIES_COLLECTION, embedding_model, openai_client, S3_BUCKET_NAME, S3_REGION, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, S3_REGION, S3_BUCKET_NAME
from datetime import datetime, timezone, timedelta
import pycountry_convert as pc
import pandas as pd
import boto3, os, pytz
from botocore.exceptions import ClientError
import re

def build_claim_embedding_text(row):
    def is_known(value):
        return value and str(value).strip().lower() not in ["undetermined", "nan", "none", "null", ""]
    parts = []

    # --- Incident summary ---
    raw_date = row['Incident Date']
    try:
        dt = datetime.fromisoformat(str(raw_date).split("T")[0])
        date_str = dt.strftime("%B %d, %Y")
    except Exception:
        date_str = raw_date  # fallback to original if parsing fails

    summary = []
    if date_str:
        summary.append(f"On {date_str}")
    if is_known(row.get("Client Name")):
        summary.append(f"{row['Client Name']}")
    else:
        summary.append("an unidentified client")
    if is_known(row.get("Country (Set ID)")):
        summary.append(f"in {row['Country (Set ID)']}")
    if is_known(row.get("Industry")):
        summary.append(f"from the {row['Industry']} industry")
    incident_intro = " ".join(summary) + " experienced an incident."
    parts.append(incident_intro)

    # --- Cause & description ---
    if is_known(row.get("Cause")):
        parts.append(f"Cause: {row['Cause']}")
    if is_known(row.get("Brief Description of Incident")):
        parts.append(f"Incident Description: {row['Brief Description of Incident']}")

    # --- Claim details ---
    claim_lines = []
    if is_known(row.get("Type of Claim")):
        claim_lines.append(f"- Type of Claim: {row['Type of Claim']}")
    if is_known(row.get("Sub Type of Claim")):
        claim_lines.append(f"- Subtype: {row['Sub Type of Claim']}")
    if is_known(row.get("Loss Details")):
        claim_lines.append(f"- Loss Details: {row['Loss Details']}")
    if is_known(row.get("Remarks")):
        claim_lines.append(f"- Remarks: {row['Remarks']}")
    if is_known(row.get("Additional Long Remarks")):
        claim_lines.append(f"- Additional Notes: {row['Additional Long Remarks']}")

    if claim_lines:
        parts.append("\nClaim Details:\n" + "\n".join(claim_lines))

    return "\n".join(parts)

def get_embedding(text):
    embedding = openai_client.embeddings.create(
        input=[text],
        model=embedding_model
    ).data[0].embedding
    return embedding

def country_to_region(country_name):
    hardcoded = {'Iran (Islamic Republic of)': 'Iran',
            'Korea (the Republic of)': 'South Korea',
            'Korea': 'South Korea',
            'Viet Nam' : 'Vietnam',
            'Taiwan (Province of China)': 'Taiwan',
            'Venezuela (Bolivarian Republic of)' : 'Venezuela',
            'Moldova (the Republic of)': 'Moldova',
            'Lebanon ': 'Lebanon',
            'Bolivia (Plurinational State of)': 'Bolivia',
            "Korea (the Democratic People's Republic of)" : 'North Korea',
            "Saint Thomas": 'United States of America',
            'European Union' : 'Spain',
            'Kosovo' : 'Russia',
            'Holy See' : 'Italy'
            }
    if country_name in hardcoded:
        country_name = hardcoded[country_name]

    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        continents = {
            "AF": "Africa",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "OC": "Oceania",
            "SA": "South America"
        }
        return continents[continent_code]
    except:
        return "Unknown"
    

def marsh_data_process(marsh_data):
    marsh_data['Region'] = marsh_data["Country (Set ID)"].apply(country_to_region)
    marsh_data['embedding_text'] = marsh_data.apply(build_claim_embedding_text, axis=1)
    marsh_data["vector_embedding"] = marsh_data["embedding_text"].apply(get_embedding)

    return marsh_data


def upsert_mongo(df):
  #Change Date Type
  date_columns = ["Incident Date", "Date Reported to Insurer"]
  for col in date_columns:
      df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

  for _, row in df.iterrows():
      claim_number = str(row["Claim Number"])
      document = row.to_dict()
      industry_value = row["Industry"]

      # Move Claim Number to _id field
      document["_id"] = claim_number
      document.pop("Claim Number", None) 

      # Upsert (update if exists, insert if not)
      PROPRIETARY_COLLECTION.update_one(
          {"_id": claim_number},
          {"$set": document},
          upsert=True
      )
      
      # Update Industries collection
      INDUSTRIES_COLLECTION.update_one(
          {"industry": industry_value},     
          {"$setOnInsert": {"industry": industry_value}},
          upsert=True
      )


def save_to_s3_bytes(file_bytes, filename):
    s3 = boto3.resource(
        service_name='s3',
        region_name=S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    extension = os.path.splitext(filename)[1]
    timezone = pytz.timezone("Asia/Singapore")
    timestamp = datetime.now(timezone).strftime("%d-%m-%Y-%H%M%S") 
    #timestamp = datetime.now(timezone.utc).strftime("%d-%m-%Y-%H%M%S")
    s3_key = f"propdata/{timestamp}_PropData{extension}"
    try:
        s3.Bucket(S3_BUCKET_NAME).put_object(Key=s3_key, Body=file_bytes)
        print(f"Uploaded '{filename}' as '{s3_key}'")
        return s3_key
    except Exception as e:
        print("S3 upload failed:", e)


def list_files_with_urls(bucket_name=S3_BUCKET_NAME, prefix="propdata/", expiration=604800): #7 days
    s3_client = boto3.client(
        service_name='s3',
        region_name=S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = []

        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                if key.endswith("/"):
                    continue

                filename = key.split("/")[-1]

                # 🔹 Extract datetime from filename (format: dd-mm-yyyy-hhmmss_PropData.xlsx)
                match = re.match(r"(\d{2}-\d{2}-\d{4})-(\d{6})", filename)
                parsed_dt = None

                if match:
                    date_part, time_part = match.groups()
                    try:
                        # Parse into UTC datetime first
                        dt = datetime.strptime(f"{date_part}-{time_part}", "%d-%m-%Y-%H%M%S")
                        parsed_dt = dt.replace(tzinfo=timezone.utc)
                        uploaded_at = parsed_dt.strftime("%Y-%m-%d %H:%M:%S (SGT)")
                    except ValueError:
                        uploaded_at = "Unknown"
                else:
                    uploaded_at = "Unknown"

                # 🔹 Generate presigned URL
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket_name, "Key": key},
                    ExpiresIn=expiration
                )

                files.append({
                    "filename": filename,
                    "s3_key": key,
                    "url": url,
                    "uploaded_at": uploaded_at,
                    "uploaded_dt": parsed_dt  # keep for sorting
                })

        # 🔹 Sort newest first (descending)
        files.sort(
            key=lambda x: x["uploaded_dt"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True
        )

        # Remove helper field before returning
        for f in files:
            f.pop("uploaded_dt", None)

        return files

    except Exception as e:
        print(f"Error listing files: {e}")
        return []
