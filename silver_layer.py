import json
import hashlib
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
BRONZE_CONTAINER = "bronze"
SILVER_CONTAINER = "silver"

def get_record_hash(record):
    hash_fields = str(record.get("CUSTOMER_NAME", "")) + \
                  str(record.get("EMAIL_ID", "")) + \
                  str(record.get("PHONE_NUMBER", "")) + \
                  str(record.get("CITY", "")) + \
                  str(record.get("STATE", "")) + \
                  str(record.get("COUNTRY", "")) + \
                  str(record.get("CUSTOMER_SEGMENT", ""))
    return hashlib.md5(hash_fields.encode()).hexdigest()

def process_record(record, file_name):
    load_ts = record.get("LOAD_TIMESTAMP", datetime.now().isoformat())
    load_dt = datetime.fromisoformat(load_ts)
    return {
        "CUSTOMER_ID": record.get("CUSTOMER_ID"),
        "CUSTOMER_NAME": record.get("CUSTOMER_NAME"),
        "EMAIL_ID": record.get("EMAIL_ID"),
        "PHONE_NUMBER": str(record.get("PHONE_NUMBER", "")),
        "CITY": record.get("CITY"),
        "STATE": record.get("STATE"),
        "COUNTRY": record.get("COUNTRY"),
        "CUSTOMER_SEGMENT": record.get("CUSTOMER_SEGMENT"),
        "CUSTOMER_STATUS": record.get("CUSTOMER_STATUS"),
        "CREDIT_RATING": record.get("CREDIT_RATING"),
        "SOURCE_SYSTEM": record.get("SOURCE_SYSTEM"),
        "FILE_NAME": file_name,
        "LOAD_YEAR": load_dt.year,
        "LOAD_MONTH": load_dt.month,
        "LOAD_DAY": load_dt.day,
        "LOAD_DAY_NAME": load_dt.strftime("%a"),
        "LOAD_QUARTER": (load_dt.month - 1) // 3 + 1,
        "RECORD_HASH": get_record_hash(record),
        "EFF_START_DT": load_ts,
        "EFF_END_DT": "9999-12-31T00:00:00",
        "IS_CURRENT": True
    }

def bronze_to_silver():
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    bronze_client = blob_service.get_container_client(BRONZE_CONTAINER)
    silver_client = blob_service.get_container_client(SILVER_CONTAINER)

    silver_records = {}
    blobs = list(bronze_client.list_blobs())
    print(f"Total {len(blobs)} files Bronze mein mili")

    for blob in blobs:
        file_name = blob.name
        print(f"Processing: {file_name}")
        blob_data = bronze_client.get_blob_client(file_name).download_blob().readall()
        
        text = blob_data.decode("utf-8").strip()
        try:
            records = json.loads(text)
            if isinstance(records, dict):
                records = [records]
        except json.JSONDecodeError:
            records = [json.loads(line) for line in text.splitlines() if line.strip()]

        for record in records:
            cid = record.get("CUSTOMER_ID")
            if not cid:
                continue
            processed = process_record(record, file_name)
            if cid in silver_records:
                existing = silver_records[cid]
                if existing["RECORD_HASH"] != processed["RECORD_HASH"]:
                    existing["EFF_END_DT"] = processed["EFF_START_DT"]
                    existing["IS_CURRENT"] = False
                    silver_records[cid + "_old"] = existing
                    silver_records[cid] = processed
            else:
                silver_records[cid] = processed

    output = "\n".join([json.dumps(r) for r in silver_records.values()])
    silver_blob = silver_client.get_blob_client("silver_customer_data.json")
    silver_blob.upload_blob(output.encode("utf-8"), overwrite=True)
    print(f"Silver layer complete - {len(silver_records)} records saved!")

if __name__ == "__main__":
    bronze_to_silver()