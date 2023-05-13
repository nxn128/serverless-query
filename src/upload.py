import click
import json
import os

# TODO: lambda wrapper should not be under a specific func
# we should use lambda layers for these shared libs
from smallquery.functions.run_query.aws.lambda_wrapper import LambdaWrapper
from smallquery.functions.upload_data.aws.s3_wrapper import S3Wrapper
from smallquery.functions.upload_data.model.upload import Upload

UPLOAD_FUNCTION_NAME = 'serverless-query-njn-UploadDataFunction'

BUCKET = 'query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed'


def save_metadata(data: dict):
    s3 = S3Wrapper()
    # os.environ['DATA_BUCKET_NAME'] = 's3://query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed'
    s3.save_metadata(BUCKET, data)


def save_table_name(table_name, to):
    # 's3://query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed/uploads/taxi_2019_04.parquet
    # os.environ['QUERY_TABLE_NAME'] = table_name
    # os.environ['QUERY_TABLE_PATH'] = f's3://query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed/{to}'
    data = {
        'table_name': table_name,
        'path': f"'s3://query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed/{to}'",
    }
    save_metadata(data)


    #with open('./table_data.json', 'w') as f:
    #    f.write(json.dumps(data))


@click.command()
@click.option(
    '--from-url',
    '-f',
    required=True,
    help='From url'
)
@click.option(
    '--to',
    '-t',
    required=True,
    help='Bucket path and filename'
)
@click.option(
    '--tablename',
    '-n',
    required=True,
    help='Friendly table name'
)
def upload(from_url: str, to: str, tablename: str):
    """
    CLI entry point function
    """
    data = Upload(from_url, to).as_dict()
    lambda_wrapper = LambdaWrapper()
    lambda_wrapper.invoke_function(UPLOAD_FUNCTION_NAME, data, True)

    save_table_name(tablename, to)

    print(f'Uploaded {from_url} to your data bucket at {to}')


if __name__ == '__main__':
    upload()
