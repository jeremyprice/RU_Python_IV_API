#!/usr/bin/env python2

from flask import Flask, url_for, jsonify, request
from utils import generate_id
from client_lib import ActiveClient


app = Flask(__name__)
active_clients = {}


@app.route('/', methods=['GET'])
def root():
    request_id = generate_id()
    client = ActiveClient(request_id)
    active_clients[request_id] = client

    title, path = client.get_next_path()
    next_url = url_for('step', step_id=path,
                       _external=True)
    output = {title: next_url, 'token': request_id}
    return jsonify(**output)


@app.route('/steps/<step_id>', methods=['POST'])
def step(step_id):
    # TODO: validate request
    # invalid token
    # invalid step
    # invalid post type
    req_json = request.get_json()
    token = req_json['token']
    client = active_clients[token]
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
    app.run(debug=True)
