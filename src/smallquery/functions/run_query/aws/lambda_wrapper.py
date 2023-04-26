import boto3
import json
from rich.console import Console


# https://docs.aws.amazon.com/code-library/latest/ug/python_3_lambda_code_examples.html
class LambdaWrapper:
    console = Console()

    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.iam_resource = boto3.resource('iam')

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
        except Exception:
            LambdaWrapper.console.print(
                f'Unable to invoke function {function_name}',
                style="bold red")
            raise
        return response
