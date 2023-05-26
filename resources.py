import datetime,pytz
from decimal import Decimal

from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from sqlalchemy import and_

from Timer import Timer
from app import db
from config import *
from models import User, ChargeRequest, WaitQueue, WaitArea
from schedule import schedule


def username_validate(value, name):
    if len(value) < 6 or len(value) > 20:
        raise ValueError(name + '长度不合法')
    return value
def password_validate(value, name):
    if len(value) < 8 or len(value) > 100:
        raise ValueError(name + '长度不合法')
    return value

class token_refresh(Resource):
    @jwt_required()
    def post(self):
        expire_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expire_time_utc = expire_time.astimezone(pytz.timezone('UTC'))
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {
          "code": 200,
          "expire": expire_time_utc.isoformat(),
          "token": access_token
        }

class user_register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=username_validate, help='username invalid must 6-20', required=True)
        parser.add_argument('password', type=password_validate, help='password invalid must 8-100', required=True)
        data = parser.parse_args()
        if User.find_by_username(data['username']):
            return {
                'code':400,
                'message': f'User {data["username"]} already exists'
            }
        new_user = User(
            username=data['username'],
            password=User.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            return {
                'code':200,
                'message': f'User {data["username"]} was created'
            }
        except:
            return {'message': 'Something went wrong'}, 500

class user_login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=username_validate, help='username invalid must 6-20', required=True)
        parser.add_argument('password', type=password_validate, help='password invalid must 8-100', required=True)
        expire_time = datetime.datetime.now() + datetime.timedelta(days=1)
        expire_time_utc = expire_time.astimezone(pytz.timezone('UTC'))
        data = parser.parse_args()
        current_user = User.find_by_username(data['username'])
        if not current_user:
            return {
                'code':400,
                'message': 'User {} doesn\'t exist'.format(data['username'])
                }
        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'code':200,
                # 'message': f'Logged in as {current_user.username}',
                "expire": expire_time_utc.isoformat(),
                "token": access_token
            }
        else:
            return {'message': 'Wrong credentials'}



class submit_charge(Resource):
    @jwt_required()
    def get(self):
        user = User.find_by_username(get_jwt_identity())
        request = db.session.query(ChargeRequest).filter(
            ChargeRequest.user_id == user.id).order_by(ChargeRequest.id.desc()).first()

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=int, help='充电量', required=True)
        parser.add_argument('fast', type=bool, help='是否快充', required=True)
        parser.add_argument('totalAmount', type=int, help='', required=True)
        data = parser.parse_args()
        user=User.find_by_username(get_jwt_identity())
        require_amount=data['amount']
        charge_mode='F' if data['fast'] else 'T'
        battery_size=data['totalAmount']
        # TODO(1): 处理，获取 charge_id
        # 判断是否不在充电状态:没有充电记录或者不存在待充电请求则代表不在充电状态
        record=db.session.query(ChargeRequest).filter_by(user_id=user.id).first()
        undo_record=db.session.query(ChargeRequest).filter(and_(ChargeRequest.user_id==user.id,ChargeRequest.state!=0)).first()
        charge_time=None
        if record is None or undo_record is None:
            # 插入对应队列
            if db.session.query(WaitQueue).filter(WaitQueue.state == 1).count() < wait_max_num:
                # 生成charge_id,加入队列
                his_front_cars = db.session.query(ChargeRequest).filter(
                    and_(ChargeRequest.charge_mode == charge_mode, ChargeRequest.state != 0)).count()
                if his_front_cars == 0:
                    charge_id = charge_mode + '1'
                else:
                    res_raw = db.session.query(ChargeRequest).filter(
                        and_(ChargeRequest.charge_mode == charge_mode, ChargeRequest.state != 0)).all()
                    res = max([int(i.charge_id[1:]) for i in res_raw])
                    charge_id = charge_mode + str(res + 1)

                if charge_mode == "F":
                    charge_time = Decimal(require_amount) / fast_power * 3600
                elif charge_mode == "T":
                    charge_time = Decimal(require_amount) / slow_power * 3600
                # 生成充电请求，插入数据库
                timer = Timer()
                submit_time = timer.get_cur_timestamp()
                charge_request = ChargeRequest(state=1, user_id=user.id, charge_mode=charge_mode,
                                               require_amount=float(require_amount), charge_time=charge_time,
                                               battery_size=float(battery_size), charge_id=charge_id,
                                               request_submit_time=submit_time)
                charge_request.save_to_db()
                wait_area = WaitArea(request_id=charge_request.id, type=charge_mode)
                wait_area.save_to_db()
                wait_queue = WaitQueue(type=charge_mode, state=1, charge_id=charge_id)
                wait_queue.save_to_db()
                success = True
                error_msg = None
                # 如果等待区不为空要调度:似乎只需要调度程序对WaitQueue中state=1的记录不断进行调度即可
                schedule(2, charge_request.id)
                state = int(db.session.query(ChargeRequest.state).filter(ChargeRequest.id == charge_request.id).scalar())
                w_area=True if state==1 else False
                c_area=True if state==2 else False
                position=db.session.query(ChargeRequest.charge_id).filter(ChargeRequest.id == charge_request.id).scalar()
                pile=db.session.query(ChargeRequest.charge_pile_id).filter(ChargeRequest.id == charge_request.id).scalar()
            else:
                success = False
                error_msg = "请求失败，等候区已满。"
                charge_id = None
        else:
            success = False
            error_msg = "请求失败，还有待完成充电请求。"
            charge_id = None
        if success:
            return {
                "amount": data['amount'],
                "chargingArea": c_area,
                "code": 200,
                "fast": data['fast'],
                "pile": pile,
                "position": position,
                "status": status[state],
                "totalAmount": data['totalAmount'],
                "waitingArea": w_area
            }
        else:
            return {
                "code": 400,
                "message": error_msg
            }
class modify_charge(Resource):
    @jwt_required()
    def post(self):
        user = db.session.query(User).filter(
            User.username == get_username(request)).first()
        charge_mode = request.json.get('charge_mode')
        require_amount = request.json.get('require_amount')
        # TODO(1): 处理，修改充电请求
        # 判断是否可以修改
        record = session.query(ChargeRequest).filter(
            and_(ChargeRequest.user_id == user.id, ChargeRequest.state == 1)).first()
        # 存在还在等候区的
        if record is not None:
            # 如果充电模式有修改则放到队列最后
            charge_id = record.charge_id
            if record.charge_mode != charge_mode:
                # WaitArea 等候区相关处理
                session.query(WaitArea).filter(
                    WaitArea.request_id == record.id).delete()
                session.add(WaitArea(request_id=record.id,
                                     type=charge_mode))
                session.commit()

                # 生成charge_id,加入队列
                his_front_cars = session.query(WaitQueue).filter(
                    WaitQueue.type == charge_mode).count()
                if his_front_cars == 0:
                    charge_id = charge_mode + '1'
                else:
                    res_raw = session.query(ChargeRequest).filter(
                        ChargeRequest.charge_mode == charge_mode).all()
                    res = max([int(i.charge_id[1:]) for i in res_raw])
                    charge_id = charge_mode + str(res + 1)
                session.query(WaitQueue).filter(WaitQueue.charge_id == record.charge_id).update({
                    "charge_id": charge_id,
                    "type": charge_mode
                })

                schedule(2, record.id)
            # 修改后数据写入数据库
            session.query(ChargeRequest).filter(ChargeRequest.id == record.id).update({
                "charge_mode": charge_mode,
                "require_amount": require_amount,
                "charge_id": charge_id
            })
            session.commit()
            success = True
            error_msg = None
        else:
            success = False
            error_msg = "修改失败，车辆不在等候区。"
        if success:
            return json({
                "code": 0,
                "message": "Success"
            })
        else:
            return json({
                "code": -1,
                "message": error_msg
            })

class sys_time(Resource):
    def get(self):
        timer = Timer()
        return {
            "time": timer.get_cur_format_time()
        }

class sys_ping(Resource):
    def get(self):
        return {
            "code": 200,
            "message": "success"
        }



















class all_users(Resource):
    @jwt_required()
    def get(self):
        return User.return_all()
    def delete(self):
        return User.delete_all()