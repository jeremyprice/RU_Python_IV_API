#!/usr/bin/env python2

from __future__ import print_function
import requests
import logging
import sys


def debug_mode():
    try:  # for Python 3
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


# debug_mode()
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "http://localhost:5000/"

# first request
first_hit = requests.get(url)
first_json = first_hit.json()
token = first_json.pop('token')
title, next_url = first_json.popitem()
print("My ID is {}".format(token))

# subsequent requests
done = False
link_titles = [title]
while not done:
    print("Accessing {}".format(next_url))
    hit = requests.post(next_url, json={'token': token})
    response = hit.json()
    if 'answer' in response:
        print(response)
        print('Link titles: {}'.format(', '.join(link_titles)))
        done = True
    else:
        token = response.pop('token')
        title, next_url = response.popitem()
        link_titles.append(title)
