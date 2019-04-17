import json
import os
import uuid

from flask import Flask, request, render_template, session, redirect, abort
from flask_cors import CORS

import settings as s
from db.db_mongo import DatabaseClient
from db.db_neo4j import Instructor, GraphDatabaseClient, Thesis

template_folder = os.path.abspath('../templates')
static_folder = os.path.abspath('../static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
CORS(app)

app.config['SECRET_KEY'] = s.SECRET_KEY

db = DatabaseClient()
client = GraphDatabaseClient()


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


@app.route('/logout')
def logout():
    user = get_current_user()

    if not user:
        return redirect('/login')

    db.user_write_session(user['_id'], '')
    return redirect('/')


@app.route('/loggedin')
def loggedin():
    user = get_current_user()

    if user:
        return str(user)
    return 'Not authenticated'


@app.route('/api/user')
def api_user():
    user = get_current_user()

    if not user:
        return abort(403)

    return json.dumps(user)


@app.route('/api/thesis/all')
def api_thesis_all():
    user = get_current_user()

    if not user:
        return abort(403)

    result = []

    query_result = client.find(Thesis.node_type)
    for i in query_result:
        result.append(i)

    return json.dumps(result)


@app.route('/api/thesis/enrol', methods=['POST'])
def enrol_thesis():
    allowed_roles = ['student']
    user = get_current_user()

    if not user or user.get('thesis_id'):
        return abort(403)

    if allowed_roles and user['role'] not in allowed_roles:
        return abort(403)

    print(request.json)
    thesis_name = request.json['thesis_name']

    db.user_enrol_thesis(user['_id'], thesis_name)
    Thesis.thesis_enrol(client, thesis_name, user['_id'])
    user['thesis_id'] = thesis_name
    return json.dumps(user)


@app.route('/api/thesis/by_instructor')
def get_thesis_by_instructor():
    allowed_roles = ['instructor']
    user = get_current_user()

    if not user:
        return abort(403)

    if allowed_roles and user['role'] not in allowed_roles:
        return abort(403)

    instructor_id = request.args['instructor_id']
    print(instructor_id)
    result = Instructor(instructor_id).get_thesis(client)
    print(result)
    return json.dumps(result)


@app.route('/api/thesis/drop_by_id', methods=['POST'])
def drop_thesis_by_id():
    allowed_roles = ['instructor']
    user = get_current_user()

    if not user:
        return abort(403)

    if allowed_roles and user['role'] not in allowed_roles:
        return abort(403)

    instructor_id = request.json['instructor_id']
    thesis_id = request.json['thesis_id']
    print(thesis_id)
    print(instructor_id)
    Instructor(instructor_id).delete_thesis(client, thesis_id)
    return 'OK'


@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    user = get_current_user()

    if not user:
        return abort(403)

    first_name = request.json['first_name']
    middle_name = request.json['middle_name']
    last_name = request.json['last_name']
    email = request.json['email']
    password = request.json.get('password', None)

    data = {
        'first_name': first_name,
        'middle_name': middle_name,
        'last_name': last_name,
        'email': email,
    }
    print('profile update')
    print(data)
    if password:
        data['password'] = password

    user = db.user_profile_update(user['_id'], data)
    return json.dumps(user)


@app.route('/api/thesis/add', methods=['POST'])
def add_thesis():
    allowed_roles = ['instructor']
    user = get_current_user()

    if not user:
        return abort(403)

    if allowed_roles and user['role'] not in allowed_roles:
        return abort(403)

    thesis_name = request.json['thesis_name']
    description = request.json['description']
    year = request.json['year']
    difficulty = request.json['difficulty']
    tags = request.json['tags']

    user = get_current_user()
    instructor = Instructor(user['_id'])
    thesis = Thesis(thesis_name=thesis_name, description=description,
                    year=year, difficulty=difficulty)
    instructor.add_thesis(client, thesis, tags)
    return 'Success'


@app.route('/')
def main():
    user = get_current_user()

    if not user:
        return redirect('/login')

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
