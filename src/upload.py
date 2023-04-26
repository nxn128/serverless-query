import click
import os

# TODO: lambda wrapper should not be under a specific func
# we should use lambda layers for these shared libs
from smallquery.functions.run_query.aws.lambda_wrapper import LambdaWrapper
from smallquery.functions.upload_data.model.upload import Upload

UPLOAD_FUNCTION_NAME = 'serverless-query-njn-UploadDataFunction'


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
def upload(from_url: str, to: str):
    """
    CLI entry point function
    """
    data = Upload(from_url, to).as_dict()
    lambda_wrapper = LambdaWrapper()
    lambda_wrapper.invoke_function(UPLOAD_FUNCTION_NAME, data, True)

    print(f'Uploaded {from_url} to your data bucket at {to}')


if __name__ == '__main__':
    upload()
