import os
import time

import config
from Timer import Timer
from exts import db
import datetime
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from finishChecker import check_finish,print_result
from resources import user_register, user_login, token_refresh, sys_time, user_charge, sys_ping, finish_charge, \
    get_single_bill, get_bills, manage_pile, get_pile_wait, get_piles, get_report
from models import Charger, User
from apscheduler.schedulers.background import BackgroundScheduler

def init_pile():
    if not db.session.query(Charger).first():
        types = ['F','F', 'T', 'T', 'T']
        for t in types:
            Charger(type=t).save_to_db()
    if not db.session.query(User).filter(User.username=='admin_bupt_10').first():
        User(username='admin_bupt_10',password=User.generate_hash('admin_bupt_10'),admin=True).save_to_db()
def run_check():
    with app.app_context():
        check_finish()
def run_print():
    with app.app_context():
        print_result()

app = Flask(__name__)
CORS(app, supports_credentials=True)
scheduler1 = BackgroundScheduler()
# scheduler2 = BackgroundScheduler()
api = Api(app)
jwt = JWTManager(app)
app.config.from_object(config)
app.config["RESTFUL_JSON"] = {"ensure_ascii": False}
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=36500)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
db.app=app
db.init_app(app)

with app.app_context():
    db.create_all()
    init_pile()
timer=Timer()
scheduler1.add_job(func=run_check, trigger='interval', seconds=1)
scheduler1.add_job(func=run_print, trigger='interval', seconds=config.print_time)
scheduler1.start()
# scheduler2.start()
api.add_resource(user_register, '/user/register')
api.add_resource(user_login, '/user/login')
api.add_resource(token_refresh, '/token/refresh')
api.add_resource(user_charge, '/charge')          #充电请求的增删改查
api.add_resource(finish_charge, '/charge/finish') #主动结束充电
api.add_resource(get_single_bill,'/charge/bill/<billId>')
api.add_resource(get_bills,'/charge/bills')
api.add_resource(manage_pile,'/pile/<int:pileId>')
api.add_resource(get_pile_wait,'/pile/<int:pileId>/wait')
api.add_resource(get_piles,'/piles')
api.add_resource(get_report,'/report')
api.add_resource(sys_time, '/time')
api.add_resource(sys_ping, '/ping')


@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=False)

