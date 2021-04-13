#!/usr/local/bin/python3

"""
Issue Picker module.
This module searches issues on Jira, using the API v3.
It relies on 4 environment variables to be set on alfred, when you
import the workflow for the first time:

domain (string): the domain that will be used to form the full Jira
    website (e.g. `jira` -> `jira.atlassian.net`)
email (string): email address connected to the personal account
api_token (string): token obtained from the API page on jira:
    https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/  # pylint: disable=line-too-long # noqa
projects (List[strings]): list of the project keys separated by a comma `,`
    used to fetch the issues from with JQL expressions (e.g. `PRJ,CAR,FRN`)
"""

import json
import logging
import os
import sys

import requests
from requests.auth import HTTPBasicAuth

MAIN_URL = f'https://{os.environ["domain"]}.atlassian.net'
REST_API_URL = MAIN_URL+'/rest/api/3/issue/picker'
AUTH = HTTPBasicAuth(os.environ['email'], os.environ['api_token'])


def get_response(query):
    """Send request and parse response"""
    headers = {'Accept': 'application/json'}
    projects = os.environ['projects'].split(',')
    query = {
        'query': query,
        'currentJQL': ' or '.join([f'project={project.strip()}'
                                   for project in projects])
    }

    response = requests.request(
        "GET", REST_API_URL, headers=headers, params=query, auth=AUTH)
    respose_json = json.loads(response.text)

    logging.debug('response: %s', response)
    logging.debug('response_json: %s', respose_json)
    logging.info('Response code: %d', response.status_code)

    return respose_json


def format_results(response, original_query):
    """Format results"""
    query = original_query.upper()
    if len(response['sections']) == 2:
        selected = sorted(response['sections'][1]['issues'],
                          key=lambda x: x['id'])
    else:
        selected = sorted(response['sections'][0]['issues'],
                          key=lambda x: x['id'])
    logging.debug('Selected: %s', [issue['key'] for issue in selected])
    items = []
    if query not in [issue['key'] for issue in selected]:
        items.append({
            'title': query,
            'subtitle': 'No results from the API. '
                        + 'Press return to open in the browser',
            'arg': f'{MAIN_URL}/browse/{query}'
        })
    items.extend([{
        'title': issue['key'],
        'subtitle': issue['summary'],
        'arg': f'{MAIN_URL}/browse/{issue["key"]}'
    } for issue in selected])

    return json.dumps({'items': items}, indent=4)


def process_query(alfred_query):
    """Entry point function"""
    if len(alfred_query) < 3:
        return json.dumps({
            'items': [{
                'title': 'write at least the first 3 letters of the project'
            }]
        })
    response = get_response(alfred_query)
    return format_results(response, alfred_query)


if __name__ == u"__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug('input: %s', sys.argv[1])
    results = process_query(alfred_query=sys.argv[1])
    sys.stdout.write(results)
