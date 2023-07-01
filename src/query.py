"""
Serverless Query CLI
"""

import click
import csv
import json
import os
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.table import Column, Table

from smallquery.functions.run_query.aws.lambda_wrapper import LambdaWrapper
from smallquery.functions.run_query.model.query import Query
from smallquery.functions.upload_data.aws.s3_wrapper import S3Wrapper

MAX_ROWS = 1000
QUERY_FUNCTION_NAME = 'serverless-query-njn-RunQueryFunction'

console = Console()


def write_to_stdout(payload: dict) -> bool:
    """
    Writes output to the terminal
    """
    try:
        if 'errorMessage' in payload:
            console.print(payload['errorMessage'],
                          style='bold red',
                          highlight=False)
            return False

        # set a min width so that the table is somewhat recognizable at small terminal widths
        cols = [Column(c, min_width=10) for c in payload['column_names']]

        result_table = Table(
            *cols,
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
    """
    Writes output to the filename in csv format
    """
    try:
        with open(filename, 'w') as f:
            writer = csv.writer(
                f,
                delimiter=',',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerow(payload['column_names'])
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
    """
    Runs interactive REPL
    """
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
    console.print('Goodbye!')


# sample query:
# SELECT * from taxi;
# SELECT * FROM 's3://query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed/uploads/taxi_2019_04.parquet';
# SELECT * FROM 'uploads/taxi_2019_04.parquet';

def get_table_mapping():
    s3 = S3Wrapper()
    md = s3.read_metadata('query-data-2ade95b0-e4b4-11ed-9186-0644e23de3ed', 'metadata/tables.json')
    return json.loads(md)


def format_query(query: str) -> str:
    # friendly_name = os.getenv('QUERY_TABLE_NAME')
    # data_location = os.getenv('QUERY_TABLE_PATH')

    metadata = get_table_mapping()

    return query.replace(metadata['table_name'], metadata['path'])


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
    """
    CLI entry point function
    """
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

    formatted_query = format_query(query)

    data = Query(formatted_query, limit).as_dict()
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
