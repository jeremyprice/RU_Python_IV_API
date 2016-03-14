#!/usr/bin/env python2

from flask import Flask, url_for, jsonify, request
import uuid

class ActiveClient(object):
    def __init__(self, my_id):
        self.my_id = my_id
        self.next_path = generate_id()
        self.path_map = {}

    def get_next_path(self, from_path=None):
        if from_path is None:
            return self.next_path
        if from_path in self.path_map:
            return self.path_map[from_path]
        else:
            new_path = generate_id()
            self.path_map[from_path] = new_path
            return new_path

    def validate_path(self, path):
        return from_path in self.path_map


def generate_id():
    return uuid.uuid4().hex


app = Flask(__name__)
active_clients = {}


@app.route('/')
def root():
    request_id = generate_id()
    next_path = generate_id()
    client = ActiveClient(request_id)
    active_clients[request_id] = client

    next_url = url_for('step', step_id=client.get_next_path(),
                             _external=True)
    return jsonify(token=request_id, next_url=next_url)

@app.route('/steps/<step_id>', methods=['POST'])
def step(step_id):
    #TODO: validate request
    # invalid token
    # invalid step
    # invalid post type
    req_json = request.get_json()
    client = active_clients[req_json['token']]
    next_url = url_for('step', step_id=client.get_next_path(step_id),
                             _external=True)
    return jsonify(next_url=next_url)

if __name__ == '__main__':
    app.run(debug=True)
