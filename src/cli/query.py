"""
Serverless Query CLI
"""

import boto3
import click
import json
from rich.console import Console
from rich.table import Table

MAX_ROWS = 1000

console = Console()


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
            console.print(f'Invoked function {function_name}', style="cyan")
        except boto3.ClientError:
            console.print(f"Couldn't invoke function {function_name}")
            raise
        return response


@click.command()
@click.option('--query', '-q', default="", help='SQL Query for execution')
@click.option('--limit', '-l', default=10,
              help='Number of rows to return, max 1000')
def query(query, limit):
    console.print(f'Executing query {query} with max rows returned = ' +
                  f'{min(limit, MAX_ROWS)}', style="magenta")
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

    result_table = Table(
        title="Query Results",
        show_header=True,
        show_lines=True,
        row_styles=["bold yellow"])
    for i, row in enumerate(payload):
        # ensure all data items are strings for printing
        str_row_data = [str(x) for x in row]
        result_table.add_row(*str_row_data)

    console.print(result_table, justify='center')


if __name__ == '__main__':
    query()
