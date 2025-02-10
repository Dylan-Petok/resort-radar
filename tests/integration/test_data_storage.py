import os
import sys

# Add the project root to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)  # this code is added so the interpreter can find the utils folder

from unittest.mock import patch
from unittest import mock
from utils.data_storage import (
    connect_snowflake,
    store_data,
    load_cleaned_data,
    store_sentiment_data,
)


@patch("praw.Reddit")
def test_store_data_success(MockRedditClass):
    """ """

    # Mock the Reddit API to raise an exception
    mock_reddit = MockRedditClass.return_value


@patch("praw.Reddit")
def test_store_data_failure(MockRedditClass):
    """
    print for now
    """
    print("print")

    # Mock the Reddit API to raise an exception
    mock_reddit = MockRedditClass.return_value


@patch("utils.data_storage.connect_snowflake")
def test_load_cleaned_data_success(mock_connect):
    print("will do later")


@patch("utils.data_storage.connect_snowflake")
def test_load_cleaned_data_failure(mock_connect):
    print("will do later")


@patch("utils.data_storage.create_engine")
@patch("pandas.DataFrame.to_sql")
def test_store_sentiment_data_success(mock_to_sql, mock_create_engine):
    print("will do later")


@mock.patch("utils.data_storage.create_engine")
@mock.patch("pandas.DataFrame.to_sql")
def test_store_sentiment_data_failure(mock_to_sql, mock_create_engine):
    print("will do later")
