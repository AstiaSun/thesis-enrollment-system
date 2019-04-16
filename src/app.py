import json
import logging

from flask import Flask, Response, request, render_template, session
from flask_cors import CORS

from db.db_mongo import DatabaseClient

import uuid
import settings as s

app = Flask(__name__)
CORS(app)

db = DatabaseClient()


def generate_id():
    return uuid.uuid4()


@app.route('/login')
def login():
    if request.type == 'GET':
        return render_template('login.html')
    elif request.type == 'POST':
        pass


@app.route('/loggedin')
def loggedin():
    return 'test'


if __name__ == '__main__':
    app.debug = True
    app.run(host=s.APP_HOST, port=s.APP_PORT)
