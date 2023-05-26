import asyncio
from flask import Flask,jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from threading import Thread

from 后端.finishChecker import check_finish
from 后端.resources import *
from 后端.models import *

def init_pile():
    if not db.session.query(Charger).first():
        types = ['F','F', 'T', 'T', 'T']
        for t in types:
            Charger(type=t).save_to_db()
def run_check():
    with app.app_context():
        asyncio.run(check_finish())

app = Flask(__name__)
CORS(app, supports_credentials=True)
api = Api(app)
jwt = JWTManager(app)
app.config.from_object(config)
app.config["RESTFUL_JSON"] = {"ensure_ascii": False}
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=36500)
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
db.app=app
db.init_app(app)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 仅在 Windows 系统上需要
asyncio_loop = asyncio.new_event_loop()
asyncio.set_event_loop(asyncio_loop)

with app.app_context():
    db.create_all()
    init_pile()
    t = Thread(target=run_check)
    t.start()
# 允许跨域请求
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#     return response

api.add_resource(user_register, '/user/register')
api.add_resource(user_login, '/user/login')
api.add_resource(token_refresh, '/token/refresh')
api.add_resource(all_users, '/users')
api.add_resource(charge, '/charge')


@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})




