#!/usr/bin/env python3

import requests
import sys
from urllib.parse import urljoin

base_url = sys.argv[1]
get_key_url = urljoin(base_url, '/get_key')
cars_url = urljoin(base_url, '/cars')

my_key = requests.get(get_key_url).json()['id']
print(my_key)
print(requests.get(cars_url).json())
print(requests.post(cars_url, json={'id':my_key}).json())
