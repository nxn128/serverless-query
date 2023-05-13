import boto3
import json
import os
import requests


class S3Wrapper:
    """
    Wraps AWS S3 interactions
    """
    BUCKET_NAME = os.getenv('DATA_BUCKET_NAME')
    metadata_path = 'metadata/table.json'

    def __init__(self):
        self._s3 = boto3.resource('s3')

    def uploadFromUrl(self, from_url: str, to_path: str):
        """
        Uploads data from an external public url into the query data bucket
        """
        try:
            r = requests.get(from_url, stream=True)
            self._s3.Bucket(S3Wrapper.BUCKET_NAME).upload_fileobj(
                r.raw, to_path)

        except Exception as e:
            print(f'unable to upload file from {from_url} to {to_path}: {e}')
            raise

    def save_metadata(self, bucket: str, data: dict):
        obj = self._s3.Object(
            bucket_name=bucket,
            key=S3Wrapper.metadata_path,
        )
        obj.put(Body=json.dumps(data))

    def read_metadata(self, bucket: str, path: str) -> str:
        obj = self._s3.Object(
            bucket_name=bucket,
            key=S3Wrapper.metadata_path,
        )
        return obj.get()['Body'].read().decode('utf-8')
