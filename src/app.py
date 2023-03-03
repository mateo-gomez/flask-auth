from flask import Flask, render_template, request, jsonify, redirect, url_for, Response,flash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash
from bson import json_util
from bson.objectid import ObjectId

from config import config
from flask_pymongo import PyMongo

from models.UserModel import UserModel

app = Flask(__name__)
app.config.from_object(config['development'])

csrf = CSRFProtect(app)
mongo = PyMongo(app)

login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return UserModel.get_by_id(mongo, id)


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username and not email and not password:
            return {'nada': 'nada'}

        hashed_password = generate_password_hash(password=password)

        user = mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })

        response = {
            'id': str(user.inserted_id),
            'username': username,
            'password': hashed_password,
            'email': email
        }

        return redirect(url_for('login'))
    else:
        return render_template('auth/signup.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        logged_user = UserModel.login(mongo.db, username, password)

        if not logged_user:
            flash('Invalid username or password')
            return render_template('auth/login.html')

        login_user(logged_user)
        return redirect(url_for('home'))
    else:
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/users', methods=['GET'])
@login_required
def users():
    users = mongo.db.users.find()

    response = json_util.dumps(users)

    return Response(response, mimetype='application/json')



@app.route('/users/<id>', methods=['GET'])
@login_required
def user(id):

    user = mongo.db.users.find_one({ '_id': ObjectId(id) })

    if not user:
        return not_found()

    response = json_util.dumps(user)

    return Response(response, mimetype='application/json')



@app.route('/users/<id>', methods=['DELETE'])
@login_required
def delete(id):
    user = mongo.db.users.find_one({ '_id': ObjectId(id)})

    if not user:
        return not_found()

    mongo.db.users.delete_one({ '_id': ObjectId(id)})

    response = json_util.dumps({
        'message': f'User {id} was deleted successfully.'
    })

    return Response(response)



@app.route('/users/<id>', methods=['PUT'])
@login_required
def update(id):
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    hashed_password = generate_password_hash(password=password)

    mongo.db.users.update_one(
        { '_id': ObjectId(id) },
        {
            '$set': {
                'username': username,
                'email': email,
                'password': hashed_password
            }
        }
    )

    user = mongo.db.users.find_one({ '_id': ObjectId(id)})

    response = json_util.dumps(user)

    return Response(response)


@app.errorhandler(404)
def not_found(error=None):
    print(error)
    return '<h1>404 not found</h1>', 404

@app.errorhandler(401)
def status_401(error=None):
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
