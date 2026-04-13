import boto3
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = "yash-bigdata-project"
S3_PREFIX = "raw/"

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
AZURE_CONTAINER = "bronze"

def s3_to_azure_bronze():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="ap-south-1"
    )

    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service.get_container_client(AZURE_CONTAINER)

    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
    files = response.get("Contents", [])
    print(f"Total {len(files)} files S3 pe mili, Azure Bronze mein copy ho rahi hain...")

    for obj in files:
        s3_key = obj["Key"]
        file_name = s3_key.split("/")[-1]
        if not file_name.endswith(".json"):
            continue
        s3_object = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        data = s3_object["Body"].read()
        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(data, overwrite=True)
        print(f"Copied: {file_name}")

    print("All files copied to Azure Bronze container successfully")

if __name__ == "__main__":
    s3_to_azure_bronze()