import boto3
import json


# https://docs.aws.amazon.com/code-library/latest/ug/python_3_lambda_code_examples.html
class LambdaWrapper:
    """
    AWS Lambda invocation wrapper
    """

    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.iam_resource = boto3.resource('iam')

    def invoke_function(self, function_name, function_params, get_log=False):
        """
        Invokes a Lambda function.
        """
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(function_params),
                LogType='Tail' if get_log else 'None')
        except Exception:
            print(f'Unable to invoke function {function_name}')
            raise
        return response
