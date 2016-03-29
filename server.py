#!/usr/bin/env python2

from flask import Flask, url_for, jsonify, request
import uuid
import datetime

class InvalidClient(Exception): pass

class ActiveClient(object):
    CLIENT_TIMEOUT = 60 # seconds
    def __init__(self, my_id):
        self.my_id = my_id
        self.first_path = generate_id()
        self.path_map = {}
        self.path_index = [self.first_path]
        self.creation_time = datetime.datetime.now()

    def get_next_path(self, from_path=None):
        if not self.is_valid():
            raise InvalidClient()
        if from_path is None:
            return self.first_path
        if from_path in self.path_map:
            return self.path_map[from_path]
        elif len(self.path_index) < len(json_link_titles):
            new_path = generate_id()
            self.path_map[from_path] = new_path
            self.path_index.append(new_path)
            return new_path
        else:
            return ''

    def get_path_depth(self, path):
        if not self.is_valid():
            raise InvalidClient()
        return self.path_index.index(path)

    def validate_path(self, path):
        if not self.is_valid():
            raise InvalidClient()
        return from_path in self.path_map

    def is_valid(self):
        delta = datetime.datetime.now() - self.creation_time
        return delta.seconds < ActiveClient.CLIENT_TIMEOUT


def generate_id():
    return uuid.uuid4().hex


app = Flask(__name__)
active_clients = {}
json_link_titles = ['next_url', 'url_no_2', 'almost_there', 'penultimate']


@app.route('/')
def root():
    request_id = generate_id()
    client = ActiveClient(request_id)
    active_clients[request_id] = client

    path = client.get_next_path()
    next_url = url_for('step', step_id=path,
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
    path = client.get_next_path(step_id)
    if path:
        next_url = url_for('step', step_id=path,
                           _external=True)
        outgoing = {json_link_titles[client.get_path_depth(path)]: next_url}
    else: # no path left, they are at the end!
        outgoing = {'answer': 42, 'greeting': 'Thanks for playing!'}
    return jsonify(**outgoing)

if __name__ == '__main__':
    app.run(debug=True)
