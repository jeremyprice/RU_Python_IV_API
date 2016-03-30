#!/usr/bin/env python2

from flask import Flask, url_for, jsonify, request, abort
from client_lib import ClientManager


app = Flask(__name__)
client_manager = ClientManager()


@app.route('/', methods=['GET'])
def root():
    client = client_manager.new_client()
    title, path = client.get_next_path()
    next_url = url_for('step', step_id=path,
                       _external=True)
    output = {title: next_url, 'token': client.id}
    return jsonify(**output)


@app.route('/steps/<step_id>', methods=['POST'])
def step(step_id):
    req_json = request.get_json()
    if req_json is None or 'token' not in req_json:
        abort(400)
    token = req_json['token']
    client = client_manager.get_client(token)
    if not client:
        abort(401)
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
