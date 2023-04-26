"""
Serverless Query CLI
"""

import click
import csv
import json
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.table import Table

from smallquery.functions.run_query.aws.lambda_wrapper import LambdaWrapper
from smallquery.functions.run_query.model.query import Query

MAX_ROWS = 1000
QUERY_FUNCTION_NAME = 'serverless-query-njn-RunQueryFunction'

console = Console()


def write_to_stdout(payload: dict) -> bool:
    try:
        result_table = Table(
            *payload['column_names'],
            title='Query Results',
            show_header=True,
            show_lines=True,
            row_styles=['bold yellow'],
            header_style='bold',
        )

        for row in json.loads(payload['results']):
            # ensure all data items are strings for printing
            str_row_data = [str(x) for x in row]
            result_table.add_row(*str_row_data)

        console.print(result_table, justify='center')
        return True
    except Exception as e:
        console.print(f'Error writing to stdout: {e}',
                      style='bold red',
                      highlight=False)
        return False


def write_to_csv(payload: dict, filename: str) -> bool:
    try:
        with open(filename, 'w') as f:
            writer = csv.writer(
                f,
                delimiter=',',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerow(payload["column_names"])
            writer.writerows(json.loads(payload['results']))

        console.print(f'Output written to {filename}',
                      style='bold green',
                      highlight=False)
        return True

    except Exception as e:
        console.print(f'Unable to write file ({filename}): {e}',
                      style='bold red',
                      highlight=False)
        return False


# https://python-prompt-toolkit.readthedocs.io/en/master/pages/tutorials/repl.html
def run_query_repl():
    session = PromptSession()

    while True:
        try:
            text = session.prompt('> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        data = Query(text, 1000).as_dict()
        lambda_wrapper = LambdaWrapper()
        res = lambda_wrapper.invoke_function(QUERY_FUNCTION_NAME, data, True)
        payload = json.loads(res['Payload'].read())
        if write_to_stdout(payload):
            console.print(
                f'Query execution time: {payload["query_ms"]}ms',
                highlight=False
            )
    console.print("Goodbye!")


@click.command()
@click.option(
    '--query',
    '-q',
    default='',
    help='SQL Query for execution',
)
@click.option(
    '--limit',
    '-l',
    default=10,
    help='Number of rows to return, max 1000',
)
@click.option(
    '--interactive',
    '-i',
    default=False,
    is_flag=True,
    help='Interactive REPL',
)
@click.option(
    '--output',
    '-o',
    default=None,
    help='Output file (csv)'
)
def query(query: str, limit: int, interactive: bool, output: str):
    if interactive:
        run_query_repl()
        return
    else:
        console.print(
            f'Executing query {query} with max rows returned = ' +
            f'{min(limit, MAX_ROWS)}',
            style='bold blue',
            highlight=False,
        )

    data = Query(query, limit).as_dict()
    lambda_wrapper = LambdaWrapper()
    res = lambda_wrapper.invoke_function(QUERY_FUNCTION_NAME, data, True)

    payload = json.loads(res['Payload'].read())
    success = False
    if not output:
        success = write_to_stdout(payload)
    else:
        success = write_to_csv(payload, output)

    if success:
        console.print(f'Query execution time: {payload["query_ms"]}ms',
                      highlight=False)


if __name__ == '__main__':
    query()
