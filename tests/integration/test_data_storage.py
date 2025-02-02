import pytest
from unittest.mock import patch
from utils.data_extraction import extract_data

@patch("praw.Reddit")
def test_data_extraction_handles_reddit_api_errors(MockRedditClass):
    """
    Test that extract_data handles Reddit API failures gracefully
    """

    #Mock the Reddit API to raise an exception
    mock_reddit = MockRedditClass.return_value