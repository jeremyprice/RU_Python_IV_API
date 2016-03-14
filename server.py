#!/usr/bin/env python2

import flask
import uuid

def generate_id():
    return uuid.uuid4().hex


app = flask.Flask(__name__)

@app.route('/')
def root():
    request_id = generate_id()
    next_path = generate_id()
    #TODO: register the id and path in the db

    next_url = flask.url_for('step', step_id=next_path, _external=True)
    return flask.jsonify(token=request_id, next_url=next_url)

@app.route('/steps/<step_id>')
def step(step_id):
    pass

if __name__ == '__main__':
    app.run(debug=True)
