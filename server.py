#!/usr/bin/env python2

from flask import Flask, url_for, jsonify, request, abort, has_request_context
from client_lib import RedisClientManager
import logging
from logging.handlers import RotatingFileHandler


app = Flask(__name__)
client_manager = RedisClientManager()


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


handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=20)
handler.setLevel(logging.INFO)
custom_format = '''%(levelname)s %(name)s %(path)s %(endpoint)s %(remote_addr)s %(access_route)s %(message)s\n%(headers)s\n%(data)s\n *******'''  # noqa E105
handler.setFormatter(CustomFormatter(fmt=custom_format))
app.logger.addHandler(handler)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route('/advanced', methods=['GET'])
def advanced():
    client = client_manager.new_client()
    title, path = client.get_next_path()
    next_url = url_for('step', step_id=path,
                       _external=True)
    app.logger.warning('client id {}'.format(client.id))
    output = {title: next_url, 'token': client.id}
    return jsonify(**output)


@app.route('/', methods=['GET'])
def root():
    client = client_manager.new_client(easy=True)
    title, path = client.get_next_path()
    next_url = url_for('step', step_id=path,
                       _external=True)
    app.logger.warning('client id {}'.format(client.id))
    output = {title: next_url, 'token': client.id}
    return jsonify(**output)


@app.route('/steps/<step_id>', methods=['POST'])
def step(step_id):
    req_json = request.get_json()
    if req_json is None or 'token' not in req_json:
        app.logger.warning('returning 400 due to no json or no token')
        abort(400)
    token = req_json['token']
    client = client_manager.get_client(token)
    if not client:
        app.logger.warning('returning 401 due to client token not in the db')
        abort(401)
    app.logger.warning('found token in db')
    next_path = client.get_next_path(step_id)
    if next_path:
        title, path = next_path
        next_url = url_for('step', step_id=path,
                           _external=True)
        outgoing = {title: next_url, 'token': token}
    else:  # no path left, they are at the end!
        outgoing = {'answer': 42, 'greeting': 'So long, and thanks for all the fish!'}
    return jsonify(**outgoing)


if __name__ == '__main__':
    app.run()
