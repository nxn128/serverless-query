import json
import os
import time
from datetime import date, datetime
from duckdb import DuckDBPyConnection, connect

from model.query import Query

DEFAULT_ROWS = 10


# Global scope is shared across lambdas while warm
# The db connection is global to improve performance
# when multiple queries come in during a short window
db_conn: DuckDBPyConnection = None


def results_serializer(data):
    """
    Converts datetimes to ISO date strings to prevent
    serialization errors
    """
    if isinstance(data, (datetime, date)):
        # TODO: timezone concerns?
        return data.isoformat()
    raise TypeError('Type %s not serializable' % type(data))


def ensure_db_connected():
    """
    Ensures there is a valid db connection since we are using a global.
    It will only be valid on warm starts.
    """
    global db_conn
    if db_conn is None:
        db_conn = connect(database=':memory:')
        # note we do not need to set aws creds because
        # lambda has correct context and IAM roles
        # commands here are per:
        # https://duckdb.org/docs/guides/import/s3_import.html
        db_conn.execute(f"""
INSTALL httpfs;
LOAD httpfs;
SET s3_region='{os.getenv('AWS_DEFAULT_REGION')}';
""")


def run_query(query: Query) -> dict:
    """
    Runs the query on the DuckDB engine and returns a dict with the data, col names
    and elapsed query time
    """
    print(f'executing query: {query.sql} with row limit: {query.limit}')
    raw = db_conn.execute(query.sql)
    start = time.time_ns()
    res = raw.fetchmany(query.limit)
    elapsed_ms = (time.time_ns() - start) / 10**6  # convert from ns to ms

    return {
        'results': json.dumps(res, default=results_serializer),
        'column_names': [x[0] for x in raw.description],
        'query_ms': elapsed_ms
    }


def lambda_handler(event: dict, _) -> str:
    """
    Called by AWS lambda
    """
    try:
        query = Query(event.get('query', None),
                      event.get('limit', DEFAULT_ROWS))
        ensure_db_connected()
        return run_query(query)

    except Exception as e:
        print(f'error running query: {e}')
        raise
