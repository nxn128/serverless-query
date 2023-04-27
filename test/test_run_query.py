from mock import Mock

import pytest

import json

from datetime import date, datetime
from src.smallquery.functions.run_query import app


@pytest.fixture()
def run_query_event():
    """
    Generates Run Query event
    """
    return {
        'query': 'select * from unit/test.parquet',
        'limit': 10,
    }


def test_results_serializer():
    a_date = date(year=2020, month=11, day=10)
    a_date_time = datetime(year=2021, month=6, day=24,
                           hour=13, minute=3, second=12, microsecond=2323)
    a_str = 'ksjdf'
    a_int = 78
    data = {
        'some_date': a_date,
        'some_date_time': a_date_time,
        'some_string': a_str,
        'some_int': a_int,
    }
    expected_json = '{"some_date": "2020-11-10", "some_date_time": "2021-06-24T13:03:12.002323", "some_string": "ksjdf", "some_int": 78}'

    actual_json = json.dumps(data, default=app.results_serializer)

    assert expected_json == actual_json


def test_handler(run_query_event):
    ensure_db_connected_mock = Mock()
    run_query_mock = Mock()
    app.ensure_db_connected = ensure_db_connected_mock
    app.run_query = run_query_mock

    app.lambda_handler(run_query_event, None)

    assert ensure_db_connected_mock.call_count == 1
    assert run_query_mock.call_count == 1
