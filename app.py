import time

import config
from exts import db
import datetime
from flask import Flask,jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from finishChecker import check_finish
from resources import user_register, user_login, token_refresh, all_users, sys_time, user_charge, sys_ping
from models import Charger, ChargeRequest
from apscheduler.schedulers.background import BackgroundScheduler

def init_pile():
    if not db.session.query(Charger).first():
        types = ['F','F', 'T', 'T', 'T']
        for t in types:
            Charger(type=t).save_to_db()
def run_check():
    with app.app_context():
        check_finish()

app = Flask(__name__)
CORS(app, supports_credentials=True)
scheduler = BackgroundScheduler()
api = Api(app)
jwt = JWTManager(app)
app.config.from_object(config)
app.config["RESTFUL_JSON"] = {"ensure_ascii": False}
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=36500)
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
db.app=app
db.init_app(app)


with app.app_context():
    db.create_all()
    init_pile()
    # t = Thread(target=run_check)
    # t.start()
scheduler.add_job(func=run_check, trigger='interval', seconds=10)
scheduler.start()

api.add_resource(user_register, '/user/register')
api.add_resource(user_login, '/user/login')
api.add_resource(token_refresh, '/token/refresh')
api.add_resource(all_users, '/users')
api.add_resource(user_charge, '/charge')
api.add_resource(sys_time, '/time')
api.add_resource(sys_ping, '/ping')


# @app.before_first_request
# def before_first_request():
#     with app.app_context():
#         thread = threading.Thread(target=check_finish)
#         thread.start()

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=False)

