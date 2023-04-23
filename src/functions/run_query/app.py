import json
import time
from datetime import date, datetime
from duckdb import DuckDBPyConnection, connect

DEFAULT_ROWS = 10
MAX_ROWS = 1000

# Global scope is shared across lambdas while warm
# The db connection is global to improve performance
# when multiple queries come in during a short window
db_conn: DuckDBPyConnection = None


class Query:
    def __init__(self, sql: str, limit: int):
        if not sql or not isinstance(sql, str):
            raise ValueError("Query is not defined or is not a string")

        self._sql = sql
        self._limit = min(int(limit), MAX_ROWS)

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def limit(self) -> int:
        return self._limit


def results_serializer(data):
    """
    Converts datetimes to ISO date strings to prevent
    serialization errors
    """
    if isinstance(data, (datetime, date)):
        # TODO: timezone concerns?
        return data.isoformat()
    raise TypeError("Type %s not serializable" % type(data))


def ensure_db_connected():
    """
    Ensures there is a valid db connection.
    """
    global db_conn
    if db_conn is None:
        db_conn = connect(database=':memory:')
        # note we do not need to set aws creds because
        # lambda has correct context and IAM roles
        # commands here are per:
        # https://duckdb.org/docs/guides/import/s3_import.html
        db_conn.execute("""
INSTALL httpfs;
LOAD httpfs;
SET s3_region='us-east-2';
""")


def run_query(query: Query) -> dict:
    print(f'executing query: {query.sql} with row limit: {query.limit}')
    raw = db_conn.execute(query.sql)
    start = time.time_ns()
    res = raw.fetchmany(query.limit)
    elapsed_ms = (time.time_ns() - start) / 10**6
    res = {
        "results": res,
        "column_names": [x[0] for x in raw.description],
        "query_ms": elapsed_ms
    }
    return res


def lambda_handler(event: dict, _) -> str:
    try:
        query = Query(event.get('query', None),
                      event.get('limit', DEFAULT_ROWS))
        ensure_db_connected()
        return json.dumps(run_query(query), default=results_serializer)

    except Exception as e:
        print(f'error running query: {e}')
        return []
