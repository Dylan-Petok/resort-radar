# tests/unit/test_data_cleaning.py
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utils.data_cleaning import clean_data, clean_text


def test_clean_text_handles_empty_and_none():
    assert (
        clean_text("") == ""
    )  # clean_text should return an empty string if given empty text
    assert clean_text(None) == ""  # clean_text should return an empty string if none


def test_clean_text_handle_lower():
    string = "hello WORLD"
    assert (
        clean_text(string) == "hello world"
    )  # checking if clean_text lowercases the text


def test_clean_handle_url():
    url = "www.example.com"
    url2 = "https://www.example.com"
    assert clean_text(url) == ""
    assert clean_text(url2) == ""


def test_clean_special_characters():
    special = "testing testing123!!!!"
    assert clean_text(special) == "testing testing"


def test_clean_remove_extra_whitespace():
    tString = "checking  string      test    remove  whitespace"
    assert clean_text(tString) == "checking string test remove whitespace"


def test_clean_text_non_english():
    non_english_text = "Bonjour le monde"
    assert (
        clean_text(non_english_text) == "bonjour le monde"
    )  # Ensure non-English text is cleaned but not filtered


def test_clean_text_only_special_characters():
    special_chars = "!@#$%^&*()"
    assert clean_text(special_chars) == ""  # Ensure only special characters are removed


def test_clean_text_mixed_content():
    mixed_content = "Check this out! http://example.com #amazing"
    assert (
        clean_text(mixed_content) == "check this out amazing"
    )  # Ensure mixed content is cleaned properly


def test_clean_data_basic():
    input_data = {
        "Resort1": [
            {
                "resort": "Resort1",
                "title": "Visit http://example.com",
                "text": "This is a test!",
                "score": 10,
                "created_utc": 123456,
            },
        ]
    }
    expected_output = {
        "Resort1": [
            {
                "resort": "Resort1",
                "title": "visit",
                "text": "this is a test",
                "score": 10,
                "created_utc": "1970-01-02 05:17",
            }
        ]
    }

    result = clean_data(input_data)
    assert result == expected_output


def test_clean_data_skip_empty_posts():
    input_data = {
        "Resort1": [
            {
                "resort": "Resort1",
                "title": "",
                "text": "",
                "score": 5,
                "created_utc": 123456,
            },
            {
                "resort": "Resort1",
                "title": "Some title",
                "text": "Some valid text",
                "score": 10,
                "created_utc": 123457,
            },
        ]
    }

    expected_output = {
        "Resort1": [
            {
                "resort": "Resort1",
                "title": "some title",
                "text": "some valid text",
                "score": 10,
                "created_utc": "1970-01-02 05:17",
            }
        ]
    }

    result = clean_data(input_data)
    assert result == expected_output


def test_clean_data_missing_fields():
    input_data = {
        "Resort1": [
            {
                "resort": "Resort1",
                "title": "Title only",
                "text": "",
                "score": 10,
                "created_utc": 123456,
            },
            {
                "resort": "Resort1",
                "title": "",
                "text": "Text only",
                "score": 15,
                "created_utc": 123457,
            },
        ]
    }
    expected_output = {
        "Resort1": [
            {
                "resort": "Resort1",
                "title": "title only",
                "text": "",
                "score": 10,
                "created_utc": "1970-01-02 05:17",
            },
            {
                "resort": "Resort1",
                "title": "",
                "text": "text only",
                "score": 15,
                "created_utc": "1970-01-02 05:17",
            },
        ]
    }
    result = clean_data(input_data)
    assert result == expected_output
