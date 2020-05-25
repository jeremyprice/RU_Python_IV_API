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
# test the GETs on /cars
print(requests.get(cars_url, headers=headers).json())
print(requests.get(cars_url).json())
new_car = {'Name': 'Blue flash',
           'Make': 'Honda',
           'Model': 'Fit',
           'Year': '2012',
           'PrimaryDriver': 'Jeremy',
           'Color': 'Blue'}
car_id = requests.post(cars_url, headers=headers, json=new_car).json()['car']
print(car_id)
print(requests.get(cars_url, headers=headers).json())
# test the GET on the /cars/<id>
car_url = '/'.join([cars_url,car_id])
car_info = requests.get(car_url, headers=headers).json()
print(car_info)
# test the PUT on /cars/<id>
car_info['Make'] = 'Ford'
car_info['Year'] = '1999'
new_car_info = requests.put(car_url, headers=headers, json=car_info).json()
print(new_car_info)
# test the DELETE on /cars/<id>
print(requests.delete(car_url, headers=headers).json())
