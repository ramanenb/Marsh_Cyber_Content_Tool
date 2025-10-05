from app.config.settings import DB, PROPRIETARY_COLLECTION, INDUSTRIES_COLLECTION, embedding_model, openai_client
from datetime import datetime, timezone
import pycountry_convert as pc
import pandas as pd

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
        return "Undetermined"
    

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