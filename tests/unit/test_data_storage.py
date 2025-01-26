# tests/unit/test_data_storage.py
import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
from unittest import mock
import pandas as pd
from utils.data_storage import store_data, load_cleaned_data, store_sentiment_data
import urllib.parse 

@mock.patch('utils.data_storage.connect_snowflake')
def test_store_data(mock_connect_snowflake):
    mock_conn = mock.Mock()
    mock_cursor = mock.Mock()
    mock_connect_snowflake.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    cleaned_results = {
        "Resort1": [
            {"resort": "Resort1", "title": "title", "text": "text", "score": 10, "created_utc": "2023-01-01 00:00:00"}
        ]
    }

    assert store_data(cleaned_results) == True
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@mock.patch('utils.data_storage.connect_snowflake')
def test_load_cleaned_data(mock_connect_snowflake):
    mock_conn = mock.Mock()
    mock_cursor = mock.Mock()
    mock_connect_snowflake.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.description = [('RESORT',), ('TITLE',), ('P_TEXT',), ('SCORE',), ('CREATED',)]
    mock_cursor.fetchall.return_value = [
        ("Resort1", "title", "text", 10, "2023-01-01 00:00:00")
    ]

    result = load_cleaned_data()
    assert not result.empty
    assert list(result.columns) == ['RESORT', 'TITLE', 'P_TEXT', 'SCORE', 'CREATED']
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@mock.patch('utils.data_storage.create_engine')
@mock.patch('utils.data_storage.pd.DataFrame.to_sql')
def test_store_sentiment_data(mock_to_sql, mock_create_engine):
    # Arrange
    mock_engine = mock.Mock()
    mock_create_engine.return_value = mock_engine

    dataframe = pd.DataFrame({
        'resort': ['Resort1'],
        'title': ['title'],
        'text': ['text'],
        'score': [10],
        'created_utc': ['2023-01-01 00:00:00']
    })

    # Configure the mock to_sql to not raise any exceptions
    mock_to_sql.return_value = None  # Simulate successful to_sql execution

    # Act
    result = store_sentiment_data(dataframe)

    # Assert
    assert result == True
    mock_create_engine.assert_called_once_with(
        f'snowflake://{os.getenv("SNOWFLAKE_USER")}:{urllib.parse.quote(os.getenv("SNOWFLAKE_PASS"))}@{os.getenv("SNOWFLAKE_ACCOUNT")}/RESORTRADAR/PUBLIC'
    )
    mock_to_sql.assert_called_once_with(
        name='sentiment_data',
        con=mock_engine,
        if_exists='replace',
        index=False
    )