from .entities.User import User
from bson.objectid import ObjectId


class UserModel:
    @classmethod
    def login(self, db, username, password):
        try:
            user_record = db.users.find_one({ "username" : username })

            if not user_record: return None

            if not User.check_password(user_record['password'], password): return None

            user = User(user_record['_id'], user_record['username'], user_record['password'], user_record['email'])

            return user

        except Exception as exception:
            raise Exception(exception)

    @classmethod
    def get_by_id(self, db, id):
        user = db.db.users.find_one({ '_id': ObjectId(id) })

        if not user: return None

        user = User(user['_id'], user['username'], user['password'], user['email'])

        return user