from model.upload import Upload
from aws.s3_wrapper import S3Wrapper


def lambda_handler(event: dict, _) -> str:
    """
    Called by AWS lambda
    """
    try:
        upload = Upload(event.get('from_url'), event.get('to_path'))
        s3Wrapper = S3Wrapper()
        s3Wrapper.uploadFromUrl(upload.from_url, upload.to_path)

        return "ok"

    except Exception as e:
        print(f'error uploading data: {e}')
        return "error"
