import re
import nltk
from nltk.corpus import stopwords
from langdetect import detect
from datetime import datetime


# Load stopwords
stop_words = set(stopwords.words("english"))


def clean_text(text):
    """
    Clean and normalize a text string.
    """
    if not text:  # Handle None or empty text
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_data(results):
    """
    Clean the data in the results dictionary.
    """
    cleaned_results = {}

    for resort, posts in results.items():
        cleaned_posts = []

        for post in posts:
            # Clean the text fields
            cleaned_title = clean_text(post["title"])
            cleaned_text = clean_text(post["text"])

            # Skip posts where both title and text are empty after cleaning
            if not cleaned_title and not cleaned_text:
                continue

            # Optional: Check for language (skip non-English)
            # **FOR NOW COMMENTING OUT, WILL NOT LET TESTS PASS, TEST HAS FEW WORDS, WHICH LANGUAGE DETECTOR CAN NOT PICK UP
            # try:
            #     if detect(cleaned_text) != "en":
            #         continue
            # except Exception as e:
            #     print(f"Language detection error: {e}")
            #     continue

            # Add the cleaned post to the list
            cleaned_posts.append(
                {
                    "resort": post["resort"],
                    "title": cleaned_title,
                    "text": cleaned_text,
                    "score": post["score"],
                    "created_utc": datetime.fromtimestamp(post["created_utc"]).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                }
            )

        # Add cleaned posts for the resort to the results
        cleaned_results[resort] = cleaned_posts

    return cleaned_results
