#!/usr/bin/env python3

from flask import Flask, url_for, jsonify, request, abort, has_request_context
import logging
from logging.handlers import RotatingFileHandler
import os
from utils import generate_id
import redis
from rest_data_structures import Car


app = Flask(__name__)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.path = request.path
            record.endpoint = request.endpoint
            record.remote_addr = request.remote_addr
            record.access_route = request.access_route
            record.headers = request.headers
            record.data = request.get_data(as_text=True)
        return super(CustomFormatter, self).format(record)


def setup_logging():
    try:
        os.mkdir('logs/')
    except FileExistsError:
        pass
    handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=20)
    handler.setLevel(logging.INFO)
    custom_format = '''%(levelname)s %(name)s %(path)s %(endpoint)s %(remote_addr)s %(access_route)s %(message)s\n%(headers)s\n%(data)s\n *******'''  # noqa E105
    handler.setFormatter(CustomFormatter(fmt=custom_format))
    app.logger.addHandler(handler)


def validate_token(func):
    def inner(*args, **kwargs):
        if 'X-Auth-Token' not in request.headers:
            return func(*args, valid_token=False, **kwargs)
        rclient = RedisClient()
        token = request.headers['X-Auth-Token']
        if rclient.validate_token(token):
            return func(*args, valid_token=token, **kwargs)
        else:
            return func(*args, valid_token=False, **kwargs)
    # change the name so Flask doesn't complain
    inner.__name__ = 'inner_{}'.format(func.__name__)
    return inner


class RedisClient(object):
    def __init__(self):
        self.redis = redis.StrictRedis()  # defaults to localhost:6379

    def init_new_token(self, token):
        self.redis.sadd('valid_tokens', token)

    def validate_token(self, token):
        return self.redis.sismember('valid_tokens', token)

    def get_item_list(self, token, type):
        key = '{}-list-{}'.format(type, token)
        return [m.decode() for m in self.redis.smembers(key)]

    def item_in_list(self, token, type, item_id):
        key = '{}-list-{}'.format(type, token)
        return self.redis.sismember(key, item_id)

    def create_item(self, token, type, item):
        # create the item in redis
        item_id = generate_id()
        item_key = '{}-{}'.format(type, item_id)
        self.redis.hset(item_key, mapping=item.get_mapping())
        # add the item to the list
        list_key = '{}-list-{}'.format(type, token)
        self.redis.sadd(list_key, item_id)
        return item_id

    def delete_item(self, token, type, item_id):
        item_key = '{}-{}'.format(type, item_id)
        self.redis.delete(item_key)
        # add the item to the list
        list_key = '{}-list-{}'.format(type, token)
        self.redis.srem(list_key, item_id)

    def get_item(self, type, item_id):
        item_key = '{}-{}'.format(type, item_id)
        return {k.decode(): v.decode() for k, v in self.redis.hgetall(item_key).items()}

    def update_item(self, type, item_id, item):
        item_key = '{}-{}'.format(type, item_id)
        self.redis.hset(item_key, mapping=item.get_mapping())


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route('/', methods=['GET'])
def root():
    output = {'/': 'rules, routes, and description',
              '/get_token': 'get an X-Auth-Token to start adding things',
              '/cars': 'a collection of the cars - send your key to get the cars for that key',
              '/appliances': 'a collection of the appliances - send your key to get the appliances for that key',
              '/pantry': 'a collection of the items in the pantry - send your key to get the items for that key'}
    return jsonify(**output)


@app.route('/get_token', methods=['GET'])
def get_token():
    rclient = RedisClient()
    new_token = generate_id()
    rclient.init_new_token(new_token)
    return jsonify({'X-Auth-Token': new_token})

@app.route('/cars', methods=['GET', 'POST', 'PUT'])
@validate_token
def cars(valid_token=False):
    if valid_token:
        # send the info for this token
        rclient = RedisClient()
        if request.method == 'GET':
            # return the list of this item
            output = {'cars': rclient.get_item_list(valid_token, 'cars')}
        elif request.method == 'POST':
            # create a new item
            req_item = request.get_json()
            new_item = Car()
            if new_item.create(req_item):
                # has all the fields we need
                item_id = rclient.create_item(valid_token, 'cars', new_item)
                output = {'car': item_id}
            else:
                # does not have the required fields
                app.logger.warning('Tried to create a Car with bad params: {}'.format(req_item))
                abort(400)
        elif request.method == 'PUT':
            # update the item
            req_item = request.get_json()
            if 'car' not in req_item:
                app.logger.warning('Did not get the car id {}'.format(req_item))
                abort(400)
            item_id = req_item['car']
            existing_item = rclient.get_item('car', item_id)
            car = Car()
            car.create(existing_item)
            car.update(req_item)
            rclient.update_item('car', item_id)
            output = dict(car=item_id, **car.get_mapping())
    else:
        # send the usage info
        output = {'usage': 'send your token in as the value with the key "X-Auth-Token" in the request headers'}
    return jsonify(**output)


@app.route('/cars/<car_id>', methods=['GET', 'PUT', 'DELETE'])
@validate_token
def car(car_id=None, valid_token=False):
    # TODO: validate the car_id
    if valid_token:
        # send the info for this token
        rclient = RedisClient()
        if not rclient.item_in_list(valid_token, 'cars', car_id):
            # this id does not exist - return an error
            app.logger.warning('Invalid car id {}'.format(car_id))
            abort(400)
        if request.method == 'GET':
            # return the info for this car
            item = rclient.get_item('cars', car_id)
            output = dict(car=car_id, **item)
        elif request.method == 'DELETE':
            # delete the given car
            rclient.delete_item(valid_token, 'cars', car_id)
            output = {'result': 'success'}
        elif request.method == 'PUT':
            # update the item
            req_item = request.get_json()
            if 'car' not in req_item:
                app.logger.warning('Did not get the car id {}'.format(req_item))
                abort(400)
            item_id = req_item['car']
            existing_item = rclient.get_item('car', item_id)
            car = Car()
            car.create(existing_item)
            car.update(req_item)
            rclient.update_item('car', item_id)
            output = dict(car=item_id, **car.get_mapping())
    else:
        # invalid token - send the usage info
        output = {'usage': 'send your token in as the value with the key "X-Auth-Token" in the request headers'}
    return jsonify(**output)


if __name__ == '__main__':
    setup_logging()
    app.run()
