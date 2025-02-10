import os
import sys

# Add the project root to sys.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)  # this code is added so the interpreter can find the utils folder

from unittest.mock import patch
from unittest import mock
from utils.data_extraction import extract_data


@patch("praw.Reddit")
def test_extract_data_integration_with_real_reddit(
    MockRedditClass,
):  # the argument passed in is the mock object class we created right above this line using the patch utlility
    """
    Test the extract_data function by mocking Reddit's API calls.
    This ensures that extract_data behaves as expected without making real API calls.
    """
    # create a mock Reddit Instance
    mock_reddit = MockRedditClass.return_value

    # Mock subreddit() method
    mock_subreddit = mock.MagicMock()
    mock_reddit.subreddit.return_value = mock_subreddit

    # define mock data (simulate top posts in the "snowboarding" subreddit)
    mock_subreddit.search.return_value = [
        mock.MagicMock(
            title="Snowboarding at Breck",
            selftext="Great day on the slopes!",
            score=100,
            created_utc=1234567,
        ),
        mock.MagicMock(
            title="Vail Resort Snowboarding",
            selftext="I love Vail, amazing snow!",
            score=150,
            created_utc=123456869,
        ),
    ]

    # Call the extract_data function which will use the mocked Reddit API
    results = extract_data(mock_reddit)

    # Validate the structure of the results
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "Breckenridge in results", "Results should contain Breckenridge resort"
    assert "Vail" in results, "Results should contain Vail resort"

    # Validate the posts for each resort
    for resort, posts in results.items():
        assert isinstance(posts, list), f"Posts for {resort} should be a list"
        assert len(posts) > 0, f"Posts for {resort} should not be empty"

        # Validate fields in the posts
        for post in posts:
            assert "title" in post, f"Post for {resort} is missing title"
            assert "text" in post, f"Post for {resort} is missing text"
            assert "score" in post, f"Post for {resort} is missing score"
            assert "created_utc" in post, f"Post for {resort} is missing created_utc"


print("Test passed: Mock Reddit API data works as expected")
