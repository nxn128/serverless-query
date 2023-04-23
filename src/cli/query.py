"""
Serverless Query CLI
"""

import boto3
import click
import json
from rich.console import Console
from rich.table import Table

MAX_ROWS = 1000


# https://docs.aws.amazon.com/code-library/latest/ug/python_3_lambda_code_examples.html
class LambdaWrapper:
    def __init__(self, lambda_client, iam_resource):
        self.lambda_client = lambda_client
        self.iam_resource = iam_resource

    def invoke_function(self, function_name, function_params, get_log=False):
        """
        Invokes a Lambda function.

        :param function_name: The name of the function to invoke.
        :param function_params: The parameters of the function as a dict.
                                This dict is serialized to JSON before
                                it is sent to Lambda.
        :param get_log: When true, the last 4 KB of the execution log are
                        included in the response.
        :return: The response from the function invocation.
        """
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(function_params),
                LogType='Tail' if get_log else 'None')
            print(f'Invoked function {function_name}')
        except boto3.ClientError:
            print(f"Couldn't invoke function {function_name}")
            raise
        return response


@click.command()
@click.option('--query', '-q', default="", help='SQL Query for execution')
@click.option('--limit', '-l', default=10,
              help='Number of rows to return, max 1000')
def query(query, limit):
    print(f'Executing query {query} with max rows returned = ' +
          f'{min(limit, MAX_ROWS)}')
    data = {
        'query': query,
        'limit': limit
    }
    lambda_wrapper = LambdaWrapper(
        boto3.client('lambda'),
        boto3.resource('iam'))
    res = lambda_wrapper.invoke_function(
        "serverless-query-RunQueryFunction",
        data,
        True)
    payload = json.loads(json.loads(res['Payload'].read()))

    result_table = Table(show_header=False)
    for row in payload:
        result_table.add_row(*[str(x) for x in row])
    console = Console()
    console.print(result_table)


if __name__ == '__main__':
    query()
