import os

import praw
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# Access variables
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")
user_agent = os.getenv("USER_AGENT")

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=username,
    password=password,
    user_agent=user_agent,
)

# Test authentication
# try:
#     print(f"Authenticated as: {reddit.user.me()}")
# except Exception as e:
#     print("Authentication failed:", e)

#     # Test subreddit data retrieval
# try:
#     subreddit = reddit.subreddit("snowboarding")
#     print(f"Top posts in r/{subreddit.display_name}:")
#     for post in subreddit.hot(limit=5):
#         print(f"- {post.title} (Score: {post.score})")
# except Exception as e:
#     print("Failed to fetch data:", e)
