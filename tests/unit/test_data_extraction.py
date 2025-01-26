# tests/unit/test_data_extraction.py
import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
from unittest import mock
import praw

from utils.data_extraction import extract_data, top_ten

# We'll reuse this helper function to build mock posts easily.
def make_mock_post(selftext, title="Fake title", score=0, created_utc=9999999999):
    """
    Creates a MagicMock representing a Reddit post/submission
    with the given attributes.
    """
    post = mock.MagicMock()
    post.selftext = selftext
    post.title = title
    post.score = score
    post.created_utc = created_utc
    return post

@mock.patch("praw.Reddit")  # no autospec=True, so we can mock subreddit() dynamically
def test_extract_data_happy_path(MockRedditClass):
    """
    Test that extract_data returns the correct structure when
    each resort has valid text posts available.
    """
    # 1) Mock out the Reddit instance
    mock_reddit = MockRedditClass.return_value

    # 2) Create a mock for the subreddit
    mock_subreddit = mock.MagicMock()

    # 3) Decide which posts we return for the search
    #    Let's say each call to search() returns 2 valid posts.
    mock_subreddit.search.return_value = [
        make_mock_post("This is a text post", title="Post title 1", score=10, created_utc=1234567890),
        make_mock_post("Another text post", title="Post title 2", score=15, created_utc=1234567891),
    ]

    # 4) Wire up the mock: reddit.subreddit(...) -> mock_subreddit
    mock_reddit.subreddit.return_value = mock_subreddit

    # 5) Call the function under test
    results = extract_data(mock_reddit)

    # 6) Assertions
    #    According to your function, there are 10 resorts in top_ten.
    assert len(results) == 10, "Should return data for exactly 10 resorts"

    for resort in top_ten:
        assert resort in results, f"Missing resort '{resort}' in results"

    # For this test, we used 2 valid posts. The function tries to get up to 5,
    # but only 2 are available from mock_subreddit.search.return_value.
    # So each resort should have 2 posts in the result.
    for resort in top_ten:
        assert len(results[resort]) == 2, f"Resort {resort} should have 2 posts"

    # Check fields in one of the resorts' first post
    breck_post = results["Breckenridge"][0]
    assert "title" in breck_post
    assert "text" in breck_post
    assert "score" in breck_post
    assert "created_utc" in breck_post
    assert "resort" in breck_post
    assert breck_post["title"] == "Post title 1"
    assert breck_post["text"] == "This is a text post"
    assert breck_post["score"] == 10
    assert breck_post["created_utc"] == 1234567890
    assert breck_post["resort"] == "Breckenridge"


@mock.patch("praw.Reddit")
def test_extract_data_skips_empty_posts(MockRedditClass):
    """
    Test that extract_data skips posts with empty selftext.
    """
    mock_reddit = MockRedditClass.return_value
    mock_subreddit = mock.MagicMock()

    # Here, we'll include 3 posts: two have empty/whitespace text, one valid
    mock_subreddit.search.return_value = [
        make_mock_post("", title="Empty text"),            # Should be skipped
        make_mock_post("   ", title="Whitespace text"),    # Should be skipped
        make_mock_post("Real post content", title="Real"), # Should be included
    ]

    mock_reddit.subreddit.return_value = mock_subreddit

    results = extract_data(mock_reddit)

    # Each resort should get only the valid posts. In this scenario, that's 1.
    for resort, posts in results.items():
        assert len(posts) == 1, f"{resort} should only have 1 valid text post"
        assert posts[0]["title"] == "Real"
        assert posts[0]["text"] == "Real post content"


@mock.patch("praw.Reddit")
def test_extract_data_limits_to_5(MockRedditClass):
    """
    Test that extract_data respects the target limit (5) even if more are available.
    """
    mock_reddit = MockRedditClass.return_value
    mock_subreddit = mock.MagicMock()

    # Provide 8 valid text posts
    mock_posts = [
        make_mock_post(f"Sample post {i}", title=f"Title {i}", score=i*10, created_utc=1000000000+i)
        for i in range(1, 9)
    ]
    mock_subreddit.search.return_value = mock_posts

    mock_reddit.subreddit.return_value = mock_subreddit

    results = extract_data(mock_reddit)

    # Even though 8 posts are returned, we only keep up to 5
    for resort, posts in results.items():
        assert len(posts) == 5, f"{resort} should have at most 5 posts stored"


@mock.patch("praw.Reddit")
def test_extract_data_handles_exceptions(MockRedditClass):
    """
    Test that if subreddit.search() raises an exception, the function doesn't crash
    and we get an empty list for that resort.
    """
    mock_reddit = MockRedditClass.return_value
    mock_subreddit = mock.MagicMock()

    # Force an exception whenever .search() is called
    mock_subreddit.search.side_effect = Exception("Reddit is down!")
    mock_reddit.subreddit.return_value = mock_subreddit

    results = extract_data(mock_reddit)

    # We expect the function to catch the exception and store []
    # for each resort
    for resort, posts in results.items():
        assert posts == [], f"{resort} should have an empty list due to exception"


@mock.patch("praw.Reddit")
def test_extract_data_query_format(MockRedditClass):
    """
    (Optional) Test that the function calls subreddit.search() with the correct query format.
    E.g., "Breck OR Breckenridge" for "Breckenridge".
    """
    mock_reddit = MockRedditClass.return_value
    mock_subreddit = mock.MagicMock()
    mock_reddit.subreddit.return_value = mock_subreddit

    # We'll just return empty data for simplicity
    mock_subreddit.search.return_value = []

    # Call the function
    extract_data(mock_reddit)

    # Now we can check how `.search(...)` was called
    # This depends on your top_ten dict in extract_data.
    # For example, "Breckenridge" -> ["Breck", "Breckenridge"] => "Breck OR Breckenridge"
    expected_calls = [
        mock.call.search(query="Breck OR Breckenridge", sort='top', limit=15),
        mock.call.search(query="Aspen OR Snowmass", sort='top', limit=15),
        mock.call.search(query="Mammoth", sort='top', limit=15),
        mock.call.search(query="Park City OR PCMR", sort='top', limit=15),
        mock.call.search(query="Vail", sort='top', limit=15),
        mock.call.search(query="Jackson OR Jackson Hole OR JHMR OR J Hole", sort='top', limit=15),
        mock.call.search(query="Lake Tahoe OR Tahoe", sort='top', limit=15),
        mock.call.search(query="Big Sky", sort='top', limit=15),
        mock.call.search(query="Killington OR Killy", sort='top', limit=15),
        mock.call.search(query="Snowbird", sort='top', limit=15),
    ]

    # We can compare the actual calls to the expected calls.
    # Note: mock_subreddit.search is called 10 times (once per resort).
    # We can do:
    mock_subreddit.search.assert_has_calls(expected_calls, any_order=False)
    # If order doesn't matter, use `any_order=True`.
