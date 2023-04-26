from model.upload import Upload
from aws.s3_helper import S3Helper


def lambda_handler(event: dict, _) -> str:
    try:
        upload = Upload(event.get('from_url'), event.get('to_path'))
        s3Helper = S3Helper()
        s3Helper.uploadFromUrl(upload.from_url, upload.to_path)

        return "ok"

    except Exception as e:
        print(f'error uploading data: {e}')
        return "error"
