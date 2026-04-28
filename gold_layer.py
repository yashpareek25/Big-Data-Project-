import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
SILVER_CONTAINER = "silver"
GOLD_CONTAINER = "gold"

def get_rating_score(credit_rating):
    scores = {"A": 100, "B": 80, "C": 60}
    return scores.get(credit_rating, 40)

def silver_to_gold():
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    silver_client = blob_service.get_container_client(SILVER_CONTAINER)
    gold_client = blob_service.get_container_client(GOLD_CONTAINER)

    print("Silver se data load ho raha hai...")
    silver_blob = silver_client.get_blob_client("silver_customer_data.json")
    silver_data = silver_blob.download_blob().readall()
    lines = silver_data.decode("utf-8").splitlines()
    print(f"Total {len(lines)} records mile")

    dim_records = []
    fact_records = []
    CHUNK_SIZE = 10000

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        record = json.loads(line)
        if not record.get("IS_CURRENT"):
            continue

        dim_records.append({
            "CUSTOMER_ID": record.get("CUSTOMER_ID"),
            "CUSTOMER_NAME": record.get("CUSTOMER_NAME"),
            "EMAIL_ID": record.get("EMAIL_ID"),
            "CITY": record.get("CITY"),
            "STATE": record.get("STATE"),
            "COUNTRY": record.get("COUNTRY"),
            "CUSTOMER_SEGMENT": record.get("CUSTOMER_SEGMENT"),
            "CUSTOMER_STATUS": record.get("CUSTOMER_STATUS"),
            "SOURCE_SYSTEM": record.get("SOURCE_SYSTEM"),
            "FILE_NAME": record.get("FILE_NAME"),
            "LOAD_YEAR": record.get("LOAD_YEAR"),
            "LOAD_MONTH": record.get("LOAD_MONTH"),
            "LOAD_DAY": record.get("LOAD_DAY"),
            "LOAD_DAY_NAME": record.get("LOAD_DAY_NAME"),
            "LOAD_QUARTER": record.get("LOAD_QUARTER"),
            "GOLD_LOAD_TIMESTAMP": datetime.now().isoformat()
        })

        fact_records.append({
            "CUSTOMER_ID": record.get("CUSTOMER_ID"),
            "CREDIT_RATING": record.get("CREDIT_RATING"),
            "RATING_SCORE": get_rating_score(record.get("CREDIT_RATING")),
            "LOAD_YEAR": record.get("LOAD_YEAR"),
            "RECORD_START_DATE": record.get("EFF_START_DT")
        })

        if i % CHUNK_SIZE == 0:
            print(f"Processed {i} records...")

    dim_output = "\n".join([json.dumps(r) for r in dim_records])
    fact_output = "\n".join([json.dumps(r) for r in fact_records])

    gold_client.get_blob_client("dim_customer_gold.json").upload_blob(
        dim_output.encode("utf-8"), overwrite=True)
    print(f"DIM table complete - {len(dim_records)} records!")

    gold_client.get_blob_client("fact_customer_metrics_gold.json").upload_blob(
        fact_output.encode("utf-8"), overwrite=True)
    print(f"FACT table complete - {len(fact_records)} records!")

    print("Gold Layer complete!")

if __name__ == "__main__":
    silver_to_gold()