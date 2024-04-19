import boto3
import os
import argparse
from botocore import UNSIGNED
from botocore.config import Config

session = boto3.session.Session()

s3 = session.client("s3", config=Config(signature_version=UNSIGNED))

bucket_name = "mcity-safety-challenge-users"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--round_number", help="Round number to download files from"
    )
    parser.add_argument("-t", "--team_id", help="Unique team ID")
    parser.add_argument(
        "-k", "--unique_key", help="Unique key for the file to download", default=""
    )
    args = parser.parse_args()
    round_number = args.round_number
    team_id = args.team_id
    unique_key = args.unique_key

    local_download_path = "./test_data/round" + round_number
    if unique_key:
        prefix = team_id + "_" + unique_key + "/" + "round" + round_number
    else:
        prefix = team_id + "/" + "round" + round_number

    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            filename = key.split("/")[-1]
            download_path = key.replace(prefix, local_download_path)
            download_folder = os.path.dirname(download_path)
            print(download_folder, download_path)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder, exist_ok=True)

            if not key.endswith("/"):
                print(f"Downloading {key} to {download_path}")
                s3.download_file(bucket_name, key, download_path)
