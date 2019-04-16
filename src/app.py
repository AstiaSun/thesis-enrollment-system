import json
import logging

from flask import Flask, Response, request
from flask_cors import CORS

from db.db_mongo import DatabaseClient

import settings as s

app = Flask(__name__)
CORS(app)


if __name__ == '__main__':
    app.debug = True
    app.run(host=s.APP_HOST, port=s.APP_PORT)