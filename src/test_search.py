#!/usr/local/bin/python3

"""Issue Picker module tests"""

import json
import os

import pytest  # pylint: disable=unused-import


def test_search():
    """Test the parsing of the search results"""
    # set fake environment variables
    os.environ['domain'] = 'domain'
    os.environ['email'] = 'lorenzo.andraghetti@something.com'
    os.environ['api_token'] = 'XXXXXXXXXXXXXXXXXXXXX'
    os.environ['projects'] = 'PJR'

    # import the search module to initialize global variables
    import search  # pylint: disable=import-outside-toplevel

    raw_query = 'PJR-1'
    fake_response = {'sections': [{'issues': [
        {'id': '3', 'key': 'PJR-400', 'summary': 'fake issue'},
        {'id': '2', 'key': 'PJR-40', 'summary': 'fake issue'},
        {'id': '1', 'key': 'PJR-4', 'summary': 'fake issue'},
        {'id': '0', 'key': 'PJR-1', 'summary': 'fake issue'},
    ]}]}
    results_json = search.format_results(fake_response, raw_query)
    assert isinstance(results_json, str)
    results = json.loads(results_json)
    assert len(results['items']) == 4
    assert results['items'][0]['title'] == 'PJR-1'
