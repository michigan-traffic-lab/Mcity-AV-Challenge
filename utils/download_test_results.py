import boto3
import os
import argparse
from botocore import UNSIGNED
from botocore.config import Config

session = boto3.session.Session()

s3 = session.client("s3", config=Config(signature_version=UNSIGNED))

bucket_name = "mcity-safety-challenge"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--round_number", help="Round number to download files from"
    )
    parser.add_argument("-t", "--team_id", help="Unique team ID")
    args = parser.parse_args()
    round_number = args.round_number
    team_id = args.team_id

    local_download_path = "./test_data/round" + round_number
    prefix = team_id + "/" + "round" + round_number

    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            filename = key.split("/")[-1]
            download_path = os.path.join(local_download_path, filename)

            if not key.endswith("/"):
                print(f"Downloading {key} to {download_path}")
                s3.download_file(bucket_name, key, download_path)
