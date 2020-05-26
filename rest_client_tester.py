#!/usr/bin/env python3

import requests
import sys
from urllib.parse import urljoin


def test_collection(col_url, new_item, put_item, headers, singular_pre):
    # test the GETs
    print(requests.get(col_url, headers=headers).json())
    print(requests.get(col_url).json())
    item_id = requests.post(col_url, headers=headers, json=new_item).json()[singular_pre]
    print(item_id)
    print(requests.get(col_url, headers=headers).json())
    # test the GET on the /collection/<id>
    item_url = '/'.join([col_url,item_id])
    item_info = requests.get(item_url, headers=headers).json()
    print(item_info)
    # test the PUT on /collection/<id>
    put_result = requests.put(item_url, headers=headers, json=put_item).json()
    print(put_result)
    # get the newly put one to make sure
    item_info = requests.get(item_url, headers=headers).json()
    print(item_info)
    # test the DELETE on /collection/<id>
    print(requests.delete(item_url, headers=headers).json())


base_url = sys.argv[1]
get_token_url = urljoin(base_url, '/get_token')
cars_url = urljoin(base_url, '/cars')
format_url = urljoin(base_url, '/formats')
appliances_url = urljoin(base_url, '/appliances')
pantry_url = urljoin(base_url, '/pantry')

# test the format urls
print(requests.get(format_url).json())
for format in ['car', 'appliance', 'pantry']:
    print(requests.get('/'.join([format_url, format])).json())

my_token = requests.get(get_token_url).json()['X-Auth-Token']
print(my_token)
headers = {'X-Auth-Token':my_token}

new_car = {'Name': 'Blue flash',
           'Make': 'Honda',
           'Model': 'Fit',
           'Year': '2012',
           'PrimaryDriver': 'Jeremy',
           'Color': 'Blue'}
put_car = {'Make': 'Ford',
           'Year': '1999'}
test_collection(cars_url, new_car, put_car, headers, 'car')

new_appliance = {'Make': 'LG',
                 'Model': 'LG01822',
                 'Year': '2010',
                 'Location': 'Kitchen',
                 'Color': 'Stainless',
                 'Type': 'Dishwasher'}
put_appliance = {'Model': 'HP1',
                 'Year': '2015'}
test_collection(appliances_url, new_appliance, put_appliance, headers, 'appliance')

new_pantry = {'Name': 'Oatmeal',
              'Quantity': '24',
              'Measure': 'single-serve packet',
              'ExpirationDate': '05/05/25'}
put_pantry = {'Quantity': '48',
              'ExpirationDate': '05/05/27'}
test_collection(pantry_url, new_pantry, put_pantry, headers, 'pantry_item')
