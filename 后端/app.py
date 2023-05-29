import config
from exts import db
import datetime
from flask import Flask, jsonify, request
from flask_restful import Api, reqparse
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from finishChecker import check_finish
from resources import user_register, user_login, token_refresh, sys_time, user_charge, sys_ping, finish_charge, \
    get_single_bill, get_bills
from models import Charger, User
from apscheduler.schedulers.background import BackgroundScheduler

def init_pile():
    if not db.session.query(Charger).first():
        types = ['F','F', 'T', 'T', 'T']
        for t in types:
            Charger(type=t).save_to_db()
    if not db.session.query(User).filter(User.username=='admin_bupt_10').first():
        User(username='admin_bupt_10',password='admin_bupt_10',admin=True).save_to_db()
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
api.add_resource(user_charge, '/charge')          #充电请求的增删改查
api.add_resource(finish_charge, '/charge/finish') #主动结束充电
api.add_resource(get_single_bill,'/charge/bill/<int:billId>')
api.add_resource(get_bills,'/charge/bills')
api.add_resource(sys_time, '/time')
api.add_resource(sys_ping, '/ping')


@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=False)

