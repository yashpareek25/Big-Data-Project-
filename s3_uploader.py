import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class S3Uploader:
    def __init__(self, region="ap-south-1"):
        self.region = region
        self.s3 = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    def create_bucket(self, bucket_name):
        try:
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": self.region
                }
            )
            print(f"Bucket '{bucket_name}' created successfully")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["BucketAlreadyOwnedByYou", "BucketAlreadyExists"]:
                print(f"Bucket '{bucket_name}' already exists")
            else:
                print(f"Bucket creation failed: {e}")

    def upload_file(self, file_path, bucket_name, s3_key):
        try:
            self.s3.upload_file(file_path, bucket_name, s3_key)
            print(f"Uploaded: {s3_key}")
        except ClientError as e:
            print(f"Upload failed: {e}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")

    def upload_folder(self, folder_path, bucket_name, s3_prefix="raw/"):
        self.create_bucket(bucket_name)
        files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
        print(f"Total {len(files)} JSON files found, uploading...")
        for file_name in files:
            full_path = os.path.join(folder_path, file_name)
            s3_key = s3_prefix + file_name
            self.upload_file(full_path, bucket_name, s3_key)
        print("All files uploaded successfully")

if __name__ == "__main__":
    BUCKET_NAME = "yash-bigdata-project"
    FOLDER_PATH = r"C:\Users\yash pareek\Downloads\jsons (1)\jsons"
    
    uploader = S3Uploader()
    uploader.upload_folder(FOLDER_PATH, BUCKET_NAME)