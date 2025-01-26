# tests/unit/test_data_cleaning.py

import pytest
from unittest import mock
import praw
from utils.data_cleaning import clean_data, clean_text

def test_clean_text_handles_empty_and_none():
    assert clean_text("") == "" #clean_text should return an empty string if given empty text
    assert clean_text(None) == "" #clean_text should return an empty string if none

def test_clean_text_handle_lower():
    string = "hello WORLD"
    assert clean_text(string) == "hello world" #checking if clean_text lowercases the text

def test_clean_handle_url():
    url = 'www.example.com'
    url2 = 'https://www.example.com'
    assert clean_text(url) == ''
    assert clean_text(url2) == ''

def test_clean_special_characters():
    special = "testing testing123!!!!"
    assert clean_text(special) == 'testing testing'

def test_clean_remove_extra_whitespace():
    tString = 'checking  string      test    remove  whitespace'
    assert clean_text(tString) == 'checking string test remove whitespace'


def test_clean_data_basic():
    input_data = {"Resort1": [{"resort": "Resort1", "title": "Visit http://example.com", "text": "This is a test!", "score": 10, "created_utc": 123456},]}
    expected_output = {"Resort1": [{"resort": "Resort1", "title": "visit", "text": "this is a test", "score": 10, "created_utc": "1973-11-29 21:00:56"}]}

    result = clean_data(input_data)
    assert result == expected_output

def test_clean_data_skip_empty_posts():
    input_data = {
        "Resort1": [{"resort": "Resort1", "title": "", "text": "", "score": 5, "created_utc": 123456},
            {"resort": "Resort1", "title": "Some title", "text": "Some valid text", "score": 10, "created_utc": 123457},]}

    expected_output = {"Resort1": [{"resort": "Resort1", "title": "some title", "text": "some valid text", "score": 10, "created_utc": "1973-11-29 21:00:57"}]}

    result = clean_data(input_data)
    assert result == expected_output



