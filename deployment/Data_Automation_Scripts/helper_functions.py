import openai
from openai import OpenAI
import pandas as pd
import pycountry_convert as pc
import boto3
import json
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

INDUSTRY_MAPPING = {
    "Public Administration": "Public Entity & Not for Profit",
    "Health Care and Social Assistance": "HealthCare",
    "Finance and Insurance": "Financial Institutions",
    "Finance and insurance": "Financial Institutions",
    "Educational Services": "Education",
    "Professional, Scientific, and Technical Services": "Professional Services",
    "Information": "Communications, Media & Technology",
    "Manufacturing": "Manufacturing",
    "Transportation and Warehousing": "Transportation",
    "Other Services (except Public Administration)": "Other Services",
    "Retail Trade": "Retail / Wholesale",
    "Utilities": "Power & Utility",
    "Wholesale Trade": "Retail / Wholesale",
    "Real Estate and Rental and Leasing": "Real Estate",
    "Construction": "Construction",
    'Not Available': 'Misc. Other',
    'Undetermined': 'Misc. Other'
}

REGION_MAPPING = {'Iran (Islamic Republic of)': 'Iran',
             'Korea (the Republic of)': 'South Korea',
             'Viet Nam' : 'Vietnam',
             'Taiwan (Province of China)': 'Taiwan',
             'Venezuela (Bolivarian Republic of)' : 'Venezuela',
             'Moldova (the Republic of)': 'Moldova',
             'Lebanon ': 'Lebanon',
             'Bolivia (Plurinational State of)': 'Bolivia',
             "Korea (the Democratic People's Republic of)" : 'North Korea',
             "Saint Thomas": 'United States of America',
             'European Union' : 'Spain',
             'Kosovo' : 'Serbia',
             'Holy See' : 'Italy'
             }

def get_secret(secret_name):
    client = boto3.client("secretsmanager", region_name = "ap-southeast-1")
    response = client.get_secret_value(SecretId=secret_name)
    secret_dict = json.loads(response["SecretString"])
    return secret_dict

def init_openai_client():
    secret_name = os.environ["SECRET_NAME"]
    secrets = get_secret(secret_name)
    OPENAI_API_KEY = secrets["OPENAI_API_KEY"]
    #OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return client

def download_maryland_data():
    url = "https://cissm.umd.edu/research-impact/publications/cyber-events-database-home"
    DOWNLOAD_DIR = "maryland_data_test.xlsx"

    print("Fetching page...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    link_tag = soup.select_one("a.link--cta")
    if not link_tag or "href" not in link_tag.attrs:
        raise Exception("Download link not found on page")

    download_url = link_tag["href"]
    print(f"Found download link: {download_url}")

    print("Downloading Excel file...")
    data = requests.get(download_url, timeout=60)
    data.raise_for_status()

    with open(DOWNLOAD_DIR, "wb") as f:
        f.write(data.content)

    print(f"Download complete: {DOWNLOAD_DIR}")
    return DOWNLOAD_DIR


def clean_data(df, filter_start, filter_end):
    print("Filtering dates")
    filter_start =  datetime.strptime(filter_start, '%d/%m/%Y')
    filter_end = datetime.strptime(filter_end, '%d/%m/%Y')
    print("Transforming date")
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    print("Filter by event date")
    maryland = df[df['event_date'] >= filter_start]
    maryland = maryland[maryland['event_date'] <= filter_end]

    required_columns = ['event_date', 'affected_country', 'affected_organization',
                        'affected_industry', 'event_type', 'event_subtype', 'motive',
                        'description', 'actor', 'actor_type', 'actor_country', 'source_url']

    maryland.rename({"country": "affected_country",
                        "organization": "affected_organization",
                        "industry": "affected_industry",
                        }, axis=1, inplace = True)

    maryland = maryland[required_columns]
    maryland = maryland.drop_duplicates()

    return maryland

def clean_industries(maryland, industry_list):
    classified_results = {}

    for index, row in maryland.iterrows():
        raw_industry = row["affected_industry"]

        if raw_industry not in industry_list:
            if raw_industry in classified_results:
                classified = classified_results[raw_industry]
            else:
                prompt = f"""
                You are classifying industries into existing categories.

                Known industry categories:
                {industry_list}

                Given this industry name: "{raw_industry}"
                Choose the single most appropriate category from the list above.
                If it truly doesn't fit any, respond with "Misc. Other".
                Just respond with the category name, nothing else.
                """
                response = init_openai_client().chat.completions.create(
                    model="gpt-4o-mini",  
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                classified = response.choices[0].message.content.strip()

                classified_results[raw_industry] = classified

            maryland.loc[index, "affected_industry"] = classified
            print(f"Changed {raw_industry} to {classified}")

def build_embedding_text(row):
    def is_known(value):
        if not value or pd.isna(value):
            return False
        else:
            return value and value.strip().lower() != 'undetermined'

    raw_date = row['event_date']
    try:
        date_str = raw_date.strftime("%B %d, %Y")
    except Exception:
        date_str = raw_date 
    org = row['affected_organization']
    country = row['affected_country']
    industry = row['affected_industry']
    event_type = row['event_type']
    event_subtype = row['event_subtype']
    motive = row['motive']
    actor = row['actor']
    actor_type = row['actor_type']
    actor_country = row['actor_country']
    description = row['description']
    parts = []

    # --- Incident summary ---
    summary = f"On {date_str}, threat actors targeted"
    if is_known(org):
        summary += f" {org}"
    else:
        summary += " an unidentified organization"
    if is_known(country):
        summary += f", based in {country}"
    if is_known(industry):
        summary += f", operating in the '{industry}' industry"
    summary += "."
    parts.append(summary)
    # --- Event details ---
    event_lines = []
    if is_known(event_type):
        event_lines.append(f"- Event type: {event_type}")
    if is_known(event_subtype):
        event_lines.append(f"- Subtype: {event_subtype}")
    if is_known(motive):
        event_lines.append(f"- Motive: {motive}")
    if event_lines:
        parts.append("\nEvent details:\n" + "\n".join(event_lines))
    # --- Threat actor ---
    actor_lines = []
    if is_known(actor_type):
        actor_lines.append(f"- Type: {actor_type}")
    if is_known(actor):
        actor_lines.append(f"- Identity: {actor}")
    if is_known(actor_country):
        actor_lines.append(f"- Country of origin: {actor_country}")
    if actor_lines:
        parts.append("\nThreat actor:\n" + "\n".join(actor_lines))
    # --- Description ---
    if is_known(description):
        parts.append("\nDescription:\n" + description.strip())


    return "\n".join(parts)

def get_embedding(text):
    embedding = init_openai_client().embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    ).data[0].embedding
    return embedding

continent_cache = {}
def country_to_region(country_name):
    country_name = country_name.strip()
    if country_name in REGION_MAPPING:
        country_name = REGION_MAPPING[country_name]
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
    except Exception:
        pass

    if country_name in continent_cache:
        return continent_cache[country_name]

    prompt = f"""
    Classify the country or region "{country_name}" into one of these continents:
    Africa, Asia, Europe, North America, Oceania, South America.
    If it’s not a country, infer its most likely continent.
    Return only the continent name, nothing else.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        continent = response.choices[0].message.content.strip()
        continent_cache[country_name] = continent
        print(f"Classified {country_name} as {continent}")
        return continent
    except Exception:
        return "Undetermined"

