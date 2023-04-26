import boto3
import os
import requests


class S3Helper:
    BUCKET_NAME = os.getenv('DATA_BUCKET_NAME')

    def __init__(self):
        self._s3 = boto3.resource('s3')

    def uploadFromUrl(self, from_url: str, to_path: str):
        try:
            r = requests.get(from_url, stream=True)
            self._s3.Bucket(S3Helper.BUCKET_NAME).upload_fileobj(
                r.raw, to_path)

        except Exception as e:
            print(f'unable to upload file from {from_url} to {to_path}: {e}')
            raise
