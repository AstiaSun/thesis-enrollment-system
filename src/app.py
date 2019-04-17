import json
import logging

from flask import Flask, Response, request, render_template, session, redirect, url_for, abort
from flask_cors import CORS

from db.db_mongo import DatabaseClient

import os
import uuid
import settings as s

template_folder = os.path.abspath('../templates')
static_folder = os.path.abspath('../static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
CORS(app)

app.config['SECRET_KEY'] = s.SECRET_KEY

db = DatabaseClient()


def generate_id():
    return uuid.uuid4()


def get_session_id():
    return session.get('id')


def get_or_set_session_id():
    session_id = get_session_id()

    if not session_id:
        session_id = generate_id()
        session['id'] = session_id

    return session_id


def get_current_user():
    session_id = get_session_id()

    user = db.user_check_session(session_id)
    return user


def authenticated(allowed_roles=None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            user = get_current_user()

            if not user:
                return redirect('/login')

            if allowed_roles and user['role'] not in allowed_roles:
                return redirect('/')

            result = function(*args, **kwargs)
            return result

        return wrapper

    return decorator


def api_authenticated(allowed_roles=None):
    def decorator(function):
        def wrapper2(*args, **kwargs):
            user = get_current_user()

            if not user:
                return abort(403)

            if allowed_roles and user['role'] not in allowed_roles:
                return abort(403)

            result = function(*args, **kwargs)
            return result

        return wrapper2

    return decorator


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session_id = get_session_id()
        if db.user_check_session(session_id):
            return redirect('/')

        return render_template('login.html')
    elif request.method == 'POST':
        session_id = get_or_set_session_id()

        email = request.form.get('email')
        password = request.form.get('password')

        user = db.user_check_password(email, password)

        if user:
            db.user_write_session(user['_id'], session_id)
            return redirect('/')
        else:  # failed to login
            return render_template('login.html', error=True)


@app.route('/loggedin')
def loggedin():
    user = get_current_user()

    if user:
        return str(user)
    return 'Not authenticated'


@app.route('/api/user')
@api_authenticated()
def api_user():
    user = get_current_user()
    return json.dumps(user)


@app.route('/')
@authenticated()
def main():
    user = get_current_user()

    return render_template('index.html', user=user)


@app.errorhandler(404)
def on_notfound(e):
    user = get_current_user()

    if not user:
        return '404'
    else:
        return render_template('index.html', user=user)


if __name__ == '__main__':
    app.debug = True
    app.run(host=s.APP_HOST, port=s.APP_PORT)
