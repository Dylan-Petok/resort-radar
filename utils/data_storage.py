
import os
import sys
import pandas as pd
# import urllib.parse
print("Interpreter:", sys.executable)
print("sys.path:", sys.path)
from google.cloud import bigquery
from dotenv import load_dotenv
import gspread
from gspread_dataframe import set_with_dataframe
# Load environment variables from .env file
load_dotenv()

# Read environment variables
PROJECT_ID = os.getenv("PROJECT_ID", "my-gcp-project")
DATASET = os.getenv("DATASET", "my_dataset")
CLEANED_TABLE = os.getenv("CLEANED_TABLE", "cleaned_posts")
SENTIMENT_TABLE = os.getenv("SENTIMENT_TABLE", "sentiment_data")

# encoded password for url
# sf_pass_e = urllib.parse.quote(sf_pass)


def get_bq_client():
    """
    Creates and returns a BigQuery client using the default credentials
    (which must be set via GOOGLE_APPLICATION_CREDENTIALS).
    """
    return bigquery.Client(project=PROJECT_ID)

def store_data(cleaned_results):
    """
    Replaces the 'store_data' function for Snowflake.
    - Builds a DataFrame from the cleaned_results dictionary.
    - Loads it into BigQuery (truncates the table each time to mimic 'TRUNCATE TABLE').
    """
    client = get_bq_client()

    # Convert your cleaned_results (dict of lists) into a DataFrame
    rows = []
    for resort, posts in cleaned_results.items():
        for post in posts:
            rows.append({
                "resort": post["resort"],
                "title": post["title"],
                "text": post["text"],
                "score": post["score"],
                "created_utc": post["created_utc"],
            })

    df = pd.DataFrame(rows)

    # Define the fully-qualified table ID: project.dataset.table
    table_id = f"{PROJECT_ID}.{DATASET}.{CLEANED_TABLE}"

    # Configure the load job to overwrite (truncate) the existing table
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    # Load DataFrame into BigQuery
    load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    load_job.result()  # Wait for the job to complete

    print("Cleaned data loaded into BigQuery successfully.")
    return True

def load_cleaned_data():
    """
    Replaces 'load_cleaned_data' for Snowflake.
    - Queries the cleaned_posts table in BigQuery and returns a DataFrame.
    """
    client = get_bq_client()

    table_id = f"{PROJECT_ID}.{DATASET}.{CLEANED_TABLE}"
    query = f"SELECT * FROM `{table_id}`"

    query_job = client.query(query)
    df = query_job.result().to_dataframe()

    print("Cleaned data loaded from BigQuery successfully.")
    return df

def store_sentiment_data(dataframe):
    """
    Replaces 'store_sentiment_data' for Snowflake.
    - Loads a pandas DataFrame into a separate table for sentiment results.
    - Overwrites (replace) the table by default. You can change to WRITE_APPEND if needed.
    """
    client = get_bq_client()
    table_id = f"{PROJECT_ID}.{DATASET}.{SENTIMENT_TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    load_job = client.load_table_from_dataframe(dataframe, table_id, job_config=job_config)
    load_job.result()

    print("Sentiment analysis data loaded into BigQuery successfully.")
    return True

def sentiment_data_to_sheets(dataframe):
    """
    Exports the sentiment analysis data to a Google Sheet.
    
    Environment Variables Needed:
      - SHEET_ID: The ID of the target Google Sheet.
      - SHEET_NAME (optional): The name of the worksheet (default is "Sheet1").
    
    The function will clear the target worksheet and overwrite it with the new data.
    Ensure that the GOOGLE_APPLICATION_CREDENTIALS environment variable is set to your service account JSON file.
    """
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    sheet_id = os.getenv("SHEET_ID")
    if not sheet_id:
        raise ValueError("SHEET_ID environment variable is not set")
    sheet_name = os.getenv("SHEET_NAME", "Sheet1")

    gc = gspread.service_account(filename=service_account_file)

    sh = gc.open_by_key(sheet_id)

    worksheet = sh.worksheet(sheet_name)

    #clear the document and write the new dataframe
    worksheet.clear()
    set_with_dataframe(worksheet, dataframe)

    return True
