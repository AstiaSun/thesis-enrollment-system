from bson.objectid import ObjectId
from pymongo import MongoClient

import settings as s


class DatabaseClient:
    def __init__(self, host=s.MONGODB_HOSTNAME, database=s.MONGODB_NAME, users_collection=s.MONGODB_USERS_COLLECTION):
        self.db = MongoClient(host=host).get_database(database)
        self.users = self.db.get_collection(users_collection)

        self.users_cache = dict()
        self.sessions_cache = dict()

    def cache_user(self, user):
        user.pop('password', None)
        user.pop('session_id', None)

        user['_id'] = str(user['_id'])

        self.users_cache[user['_id']] = user

    def user_check_password(self, email, password):
        query = {'email': email, 'password': password}

        user = self.users.find_one(query)
        if user:
            self.cache_user(user)
        return user

    def user_check_session(self, session_id):
        if not session_id:
            return None

        if session_id in self.sessions_cache:
            user_id = self.sessions_cache[session_id]
            user = self.users_cache[user_id]

            return user

        query = {'session_id': session_id}
        user = self.users.find_one(query)
        if user:
            self.cache_user(user)
        return user

    def user_write_session(self, user_id, session_id):
        query = {'_id': ObjectId(user_id)}
        update = {'$set': {'session_id': session_id}}

        self.users.find_one_and_update(query, update)
        if session_id:
            self.sessions_cache[session_id] = user_id
        else:
            keys_to_delete = []
            for key, value in self.sessions_cache.items():
                if value == user_id:
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del self.sessions_cache[key]
        return True

    def user_enrol_thesis(self, user_id, thesis_id):
        query = {'_id': ObjectId(user_id)}
        update = {'$set': {'thesis_id': thesis_id}}

        self.users.find_one_and_update(query, update)
        if user_id in self.users_cache:
            self.users_cache[user_id]['thesis_id'] = thesis_id
        return True