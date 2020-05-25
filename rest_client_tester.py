#!/usr/bin/env python3

import requests
import sys
from urllib.parse import urljoin

base_url = sys.argv[1]
get_token_url = urljoin(base_url, '/get_token')
cars_url = urljoin(base_url, '/cars')

my_token = requests.get(get_token_url).json()['X-Auth-Token']
print(my_token)
headers = {'X-Auth-Token':my_token}
print(requests.get(cars_url, headers=headers).json())
print(requests.get(cars_url).json())
new_car = {'Name': 'Blue flash',
           'Make': 'Honda',
           'Model': 'Fit',
           'Year': '2012',
           'PrimaryDriver': 'Jeremy',
           'Color': 'Blue'}
car_id = requests.post(cars_url, headers={'X-Auth-Token':my_token}, json=new_car).json()['car']
print(car_id)
print(requests.get(cars_url, headers=headers).json())
