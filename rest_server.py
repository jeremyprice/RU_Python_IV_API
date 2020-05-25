#!/usr/bin/env python3

from flask import Flask, url_for, jsonify, request, abort, has_request_context
import logging
from logging.handlers import RotatingFileHandler
import os
from utils import generate_id
import redis


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


def validate_id(func):
    def inner(*args, **kwargs):
        req_json = request.get_json()
        if req_json is None or 'id' not in req_json:
            return func(*args, valid_id=False, **kwargs)
        rclient = RedisClient()
        if rclient.validate_id(req_json['id']):
            return func(*args, valid_id=req_json['id'], **kwargs)
        else:
            return func(*args, valid_id=False, **kwargs)
    return inner


class RedisClient(object):
    def __init__(self):
        self.redis = redis.StrictRedis()  # defaults to localhost:6379

    def init_new_id(self, new_id):
        self.redis.sadd('valid_keys', new_id)

    def validate_id(self, id_check):
        return self.redis.sismember('valid_keys', id_check)

    def get_item_list(self, owner_id, type):
        key = '{}-{}'.format(type, owner_id)
        return list(self.redis.smembers(key))


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route('/', methods=['GET'])
def root():
    output = {'/': 'rules, routes, and description',
              '/get_key': 'get a key to start adding things',
              '/cars': 'a collection of the cars - send your key to get the cars for that key',
              '/appliances': 'a collection of the appliances - send your key to get the appliances for that key',
              '/pantry': 'a collection of the items in the pantry - send your key to get the items for that key'}
    return jsonify(**output)


@app.route('/get_key', methods=['GET'])
def get_key():
    rclient = RedisClient()
    new_id = generate_id()
    rclient.init_new_id(new_id)
    return jsonify({'id': new_id})


@app.route('/cars', methods=['GET', 'POST'])
@validate_id
def cars(valid_id=False):
    if valid_id:
        # send the info for this ID
        rclient = RedisClient()
        output = {'cars': rclient.get_item_list(valid_id, 'cars')}
    else:
        # send the usage info
        output = {'usage': 'send your id in as the value with the key "id" in json format'}
    return jsonify(**output)

if __name__ == '__main__':
    setup_logging()
    app.run()
