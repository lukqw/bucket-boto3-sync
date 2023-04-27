import json
import subprocess
import boto3
import os

# aws related
REGION = "eu-central-1"
ENDPOINT_URL = "http://localhost:4566"

AWS_CONFIG = {"region_name": REGION, "endpoint_url": ENDPOINT_URL}

# website config
WEBSITE_BUCKET_NAME_A = "website-a"
WEBSITE_BUCKET_NAME_B = "website-b"

def host_website_a() -> None:
    # create s3 bucket for hosting the web app
    s3 = boto3.client("s3", **AWS_CONFIG)
    s3.create_bucket(
        Bucket=WEBSITE_BUCKET_NAME_A,
        CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
    )

    # Set the bucket policy for static website hosting
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{WEBSITE_BUCKET_NAME_A}/*",
            }
        ],
    }
    s3.put_bucket_policy(Bucket=WEBSITE_BUCKET_NAME_A, Policy=json.dumps(policy))

    # Upload the website files to the bucket
    subprocess.run(f"awslocal s3 sync web/build s3://{WEBSITE_BUCKET_NAME_A}", shell=True)

    # Enable static website hosting for the bucket
    s3.put_bucket_website(
        Bucket=WEBSITE_BUCKET_NAME_A,
        WebsiteConfiguration={
            "ErrorDocument": {"Key": "index.html"},
            "IndexDocument": {"Suffix": "index.html"},
        },
    )

    # Print the URL of the static website
    print(
        f"S3 static website URL: http://{WEBSITE_BUCKET_NAME_A}.s3-website.localhost.localstack.cloud:4566"
    )

def host_website_b() -> None:
    # create s3 bucket for hosting the web app
    s3 = boto3.client("s3", **AWS_CONFIG)
    s3.create_bucket(
        Bucket=WEBSITE_BUCKET_NAME_B,
        CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
    )

    # Set the bucket policy for static website hosting
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{WEBSITE_BUCKET_NAME_B}/*",
            }
        ],
    }
    s3.put_bucket_policy(Bucket=WEBSITE_BUCKET_NAME_B, Policy=json.dumps(policy))

    folder_path = 'web/build'
    # Get a list of all files in the folder
    for subdir, dirs, files in os.walk(folder_path):
      for file in files:
          # Create the full path to the file
          file_path = os.path.join(subdir, file)
          # Create the S3 object key by removing the folder path from the file path
          object_key = os.path.relpath(file_path, folder_path)
          # Upload the file to S3
          s3.upload_file(file_path, WEBSITE_BUCKET_NAME_B, object_key)

    # Enable static website hosting for the bucket
    s3.put_bucket_website(
        Bucket=WEBSITE_BUCKET_NAME_B,
        WebsiteConfiguration={
            "ErrorDocument": {"Key": "index.html"},
            "IndexDocument": {"Suffix": "index.html"},
        },
    )

    # Print the URL of the static website
    print(
        f"S3 static website URL: http://{WEBSITE_BUCKET_NAME_B}.s3-website.localhost.localstack.cloud:4566"
    )

host_website_a()
host_website_b()