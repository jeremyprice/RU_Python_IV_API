#!/usr/bin/env python2

import requests
import sys
import logging

def debug_mode():
    try: # for Python 3
        from http.client import HTTPConnection
    except ImportError:
        from httplib import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


debug_mode()
#TODO: pull this in from command line
url = "http://localhost:5000/"

# first request
first_hit = requests.get(url)
first_json = first_hit.json()
token = first_json['token']
next_url = first_json['next_url']

# second request
second_hit = requests.post(next_url, json={'token': token})
print second_hit.json()
