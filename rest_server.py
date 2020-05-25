#!/usr/bin/env python3

from flask import Flask, url_for, jsonify, request, abort, has_request_context
import logging
from logging.handlers import RotatingFileHandler


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
    handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=20)
    handler.setLevel(logging.INFO)
    custom_format = '''%(levelname)s %(name)s %(path)s %(endpoint)s %(remote_addr)s %(access_route)s %(message)s\n%(headers)s\n%(data)s\n *******'''  # noqa E105
    handler.setFormatter(CustomFormatter(fmt=custom_format))
    app.logger.addHandler(handler)


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


if __name__ == '__main__':
    app.run()
