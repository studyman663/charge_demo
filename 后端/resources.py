import datetime,pytz
from decimal import Decimal

from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with, marshal
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from sqlalchemy import and_

from Timer import Timer
from app import db
from config import *
from models import User, ChargeRequest, WaitQueue, WaitArea, ChargeRecord, Charger, ChargeArea, ChargeWaitArea
from schedule import schedule

charge_record_fields = {
        "chargeAmount": fields.Float,
        "chargeEndTime": fields.String,
        "chargeFee": fields.Float,
        "chargeStartTime": fields.String,
        "created_at": fields.String,
        "deleted_at": fields.String,
        "id": fields.Integer,
        "pileId": fields.Integer,
        "serviceFee": fields.Float,
        "totalFee": fields.Float,
        "updated_at": fields.String,
        "userId": fields.Integer
    }
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
          "code": 0,
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
                "code": -1,
                'message': f'User {data["username"]} already exists'
            }
        new_user = User(
            username=data['username'],
            password=User.generate_hash(data['password'])
        )
        try:
            new_user.save_to_db()
            return {
                "code": 0,
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
                "code": -1,
                'message': 'User {} doesn\'t exist'.format(data['username'])
                }
        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                "code": 0,
                "expire": expire_time_utc.isoformat(),
                "token": access_token
            }
        else:
            return {'message': 'Wrong credentials'}

class user_charge(Resource):
    @jwt_required()
    def get(self):
        user = User.find_by_username(get_jwt_identity())
        request = db.session.query(ChargeRequest).filter(
            ChargeRequest.user_id == user.id).order_by(ChargeRequest.id.desc()).first()
        if request is not None:
            fast = True if request.charge_mode == 'F' else False
            w_area = True if int(request.state) == 1 else False
            c_area = True if int(request.state)== 3 or int(request.state) == 2 else False
            if w_area:
                position=int(request.charge_id[1:])
            if c_area:
                if request.state==3:
                    position=0
                else:
                    front_num = db.session.query(ChargeArea.request_id).filter(and_(ChargeArea.pile_id == request.charge_pile_id,ChargeArea.request_id<request.id)).count()
                    position=front_num+1
            if request.state==0:
                position=-1
            return {
                "amount": int(request.require_amount),
                "chargingArea": c_area,
                "code": 0,
                "fast": fast,
                "pile": int(request.charge_pile_id),
                "position": position,
                "status": status[request.state],
                "totalAmount": int(request.battery_size),
                "waitingArea": w_area
            }
        else:
            return {
                "code": -1,
                "message": '该用户无充电状态'
            }

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
                c_area=True if state==3 or state==2 else False
                if w_area:
                    position = int(charge_request.charge_id[1:])
                if c_area:
                    if charge_request.state == 3:
                        position = 0
                    else:
                        position = db.session.query(ChargeArea.request_id).filter(
                            and_(ChargeArea.pile_id == charge_request.charge_pile_id,
                                 ChargeArea.request_id < charge_request.id)).count()
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
                "code": 0,
                "fast": data['fast'],
                "pile": int(charge_request.charge_pile_id),
                "position": position,
                "status": status[state],
                "totalAmount": data['totalAmount'],
                "waitingArea": w_area
            }
        else:
            return {
                "code": -1,
                "message": error_msg
            }
    @jwt_required()
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=int, help='充电量', required=True)
        parser.add_argument('fast', type=bool, help='是否快充', required=True)
        parser.add_argument('totalAmount', type=int, help='', required=True)
        data = parser.parse_args()
        user = User.find_by_username(get_jwt_identity())
        require_amount = data['amount']
        charge_mode = 'F' if data['fast'] else 'T'
        battery_size = data['totalAmount']
        # TODO(1): 处理，修改充电请求
        # 判断是否可以修改
        record = db.session.query(ChargeRequest).filter(
            and_(ChargeRequest.user_id == user.id, ChargeRequest.state == 1)).first()
        # 存在还在等候区的
        if record is not None:
            # 如果充电模式有修改则放到队列最后
            charge_id = record.charge_id
            if record.charge_mode != charge_mode:
                # WaitArea 等候区相关处理
                db.session.query(WaitArea).filter(
                    WaitArea.request_id == record.id).delete()
                WaitArea(request_id=record.id,type=charge_mode).save_to_db()
                # 生成charge_id,加入队列
                his_front_cars = db.session.query(WaitQueue).filter(
                    WaitQueue.type == charge_mode).count()
                if his_front_cars == 0:
                    charge_id = charge_mode + '1'
                else:
                    res_raw = db.session.query(ChargeRequest).filter(
                        ChargeRequest.charge_mode == charge_mode).all()
                    res = max([int(i.charge_id[1:]) for i in res_raw])
                    charge_id = charge_mode + str(res + 1)
                db.session.query(WaitQueue).filter(WaitQueue.charge_id == record.charge_id).update({
                    "charge_id": charge_id,
                    "type": charge_mode
                })
                schedule(2, record.id)
            # 修改后数据写入数据库
            db.session.query(ChargeRequest).filter(ChargeRequest.id == record.id).update({
                "charge_mode": charge_mode,
                "require_amount": require_amount,
                "charge_id": charge_id
            })
            db.session.commit()
            state = int(db.session.query(ChargeRequest.state).filter(ChargeRequest.id == record.id).scalar())
            w_area = True if state == 1 else False
            c_area = True if state == 3 or state == 2 else False
            success = True
            error_msg = None
        else:
            success = False
            error_msg = "修改失败，车辆不在等候区。"
        if success:
            return {
                "amount": data['amount'],
                "chargingArea": c_area,
                "code": 0,
                "fast": data['fast'],
                "pile": int(record.charge_pile_id),
                "position": int(record.charge_id[1:]),
                "status": status[state],
                "totalAmount": data['totalAmount'],
                "waitingArea": w_area
            }
        else:
            return {
                "code": -1,
                "message": error_msg
            }
    @jwt_required()
    def delete(self):
        user = User.find_by_username(get_jwt_identity())
        request = db.session.query(ChargeRequest).filter(
            ChargeRequest.user_id == user.id).order_by(ChargeRequest.id.desc()).first()
        if request is None:
            success = False
            error_msg = "该用户没有充电请求"
        else:
            if request.state == 1:
                success = True
                db.session.query(ChargeRequest).filter(ChargeRequest.id == request.id).delete()
                db.session.query(WaitArea).filter(WaitArea.request_id == request.id).delete()
                db.session.query(WaitQueue).filter(WaitQueue.charge_id == request.charge_id).delete()
                db.session.commit()
            else:
                success = False
                error_msg='车辆不在等待区，取消失败'
        if success:
            return {
                "code": 0,
                "message": "取消成功"
            }
        else:
            return {
                "code": -1,
                "message": error_msg
            }
class finish_charge(Resource):
    @jwt_required()
    def post(self):
        user = User.find_by_username(get_jwt_identity())
        # TODO(2): 处理，取消充电请求
        # question：用户的最后一个请求一定是最新的要取消的请求吗？
        request = db.session.query(ChargeRequest).filter(
            ChargeRequest.user_id == user.id).order_by(ChargeRequest.id.desc()).first()
        if request is None:
            success = False
            error_msg = "该用户没有充电请求"
        else:
            # 1.生成详单
            # 生成详单前面部分
            timer = Timer()
            create_time = timer.get_cur_format_time()  # 用内置的timer类获取格式化模拟时间字符串
            now = datetime.datetime.strptime(
                create_time, "%Y-%m-%d %H:%M:%S")  # 把格式化字符串转换为datetime类以进行计算
            # "order_id": "20220101000001",
            order_id = now.strftime("%Y%m%d") + '%06d' % request.id
            record_id = str(db.session.query(ChargeRecord).count() + 1)
            # 如果当前不在充电:直接生成充电详单
            if request.state != 3:
                charge_record = ChargeRecord(id=record_id, order_id=order_id, created_at=create_time,
                                             chargeAmount='%.2f' % 0, charged_time='%.2f' % 0, chargeStartTime='%.2f' % 0,
                                             chargeEndTime='%.2f' % 0, chargeFee='%.2f' % 0, serviceFee='%.2f' % 0,
                                             totalFee='%.2f' % 0, pileId=request.charge_pile_id, userId=user.id,updated_at=create_time
                                             )
                charge_record.save_to_db()
            # 如果当前正在充电，计算后再创建充电详单 question：算法尚未测试
            else:
                begin_time = datetime.datetime.fromtimestamp(request.start_time)
                end_time = now
                charged_time = (end_time - begin_time).seconds  # 充电时长

                if request.charge_mode == "F":
                    rate = 30
                else:
                    rate = 10
                charged_amount = float('%0.2f' % (
                        charged_time / 3600 * rate))  # 充电量
                service_cost = float('%0.2f' %
                                     (0.8 * float(charged_amount)))  # 服务费用
                # 计算充电费用：将一天分成6个时间区域，只考虑24h内充完电的情况
                # 07：00 - 10：00  1  平时  0.7元/度
                # 10：00 - 15：00  2  峰时  1.0元/度
                # 15：00 - 18：00  3  平时  0.7元/度
                # 18：00 - 21：00  4  峰时  1.0元/度
                # 21：00 - 23：00  5  平时  0.7元/度
                # 23：00 - 07：00  6  谷时  0.4元/度
                clocks = [7, 10, 15, 18, 21, 23, 31]
                fees = [0.7, 1.0, 0.7, 1.0, 0.7, 0.4]
                # 判断开始时间和结束时间的 时间区域
                for i in range(len(clocks) + 1):
                    if i == 6 or clocks[i] <= begin_time.hour < clocks[(i + 1) % len(clocks)]:
                        begin_time_zone = i + 1
                        break
                for i in range(len(clocks)):
                    if i == 6 or clocks[i] <= end_time.hour < clocks[(i + 1) % len(clocks)]:
                        end_time_zone = i + 1
                        break
                # 如果开始和结束的时间区域相同
                begin_time_zone = begin_time_zone % len(clocks)
                end_time_zone = end_time_zone % len(clocks)
                if begin_time_zone == end_time_zone:
                    charging_cost = float('%.2f' % (
                            charged_amount * fees[begin_time_zone - 1]))  # 充电费用
                else:
                    # 分别计算开始时间到临界值的时间，结束时间到临界值的时间。单位为秒
                    diff_time1 = (clocks[begin_time_zone] - (
                        begin_time.hour if begin_time.hour >= 7 else (begin_time.hour + 24)) - 1) * 3600 + \
                                 (60 - begin_time.minute) * \
                                 60 + 60 - begin_time.second
                    diff_time2 = (
                                         (end_time.hour if begin_time.hour >= 7 else (begin_time.hour + 24)) - clocks[
                                     (end_time_zone - 1) % len(clocks)]) * 3600 + end_time.minute * 60 + end_time.second
                    zones = []  # 要计算的时间区域。①如果开始区域为2，结束为5，得到2、3、4、5；②如果开始为5，结束为2，得到5、6、1、2
                    if begin_time_zone < end_time_zone:
                        for i in range(begin_time_zone, end_time_zone + 1):
                            zones.append(i)
                    else:
                        for i in range(begin_time_zone, 7):
                            zones.append(i)
                        for i in range(1, end_time_zone + 1):
                            zones.append(i)
                    # 对覆盖的所有时间区域进行计算
                    for i in zones:
                        if i == begin_time_zone:
                            charging_cost = diff_time1 / 3600 * \
                                            rate * fees[i - 1]
                        elif i == end_time_zone:
                            charging_cost += diff_time2 / 3600 * \
                                             rate * fees[i - 1]
                        else:
                            charging_cost += (clocks[i] - clocks[i - 1]) * \
                                             rate * fees[i - 1]
                charging_cost = float('%.2f' % charging_cost)  # 充电费用
                total_cost = service_cost + charging_cost  # 总费用
                # 添加充电详单
                charge_record = ChargeRecord(id=record_id, order_id=order_id, created_at=create_time,
                                             chargeAmount=charged_amount, charged_time=charged_time,
                                             chargeStartTime=begin_time.strftime(
                                                 "%Y-%m-%d %H:%M:%S"),
                                             chargeEndTime=end_time.strftime(
                                                 "%Y-%m-%d %H:%M:%S"),
                                             chargeFee=charging_cost, serviceFee=service_cost,
                                             totalFee=total_cost, pileId=request.charge_pile_id, userId=user.id,updated_at=create_time
                                             )
                charge_record.save_to_db()
                # 更新充电桩信息
                charger = db.session.query(Charger).filter(
                    Charger.id == request.charge_pile_id).first()
                charger.cumulative_charging_time += charged_time
                charger.cumulative_charging_amount = '%.2f' % (
                        float(charger.cumulative_charging_amount) + charged_amount)
                charger.cumulative_usage_times += 1
                # 重新写入
                db.session.query(Charger).filter(Charger.id == request.charge_pile_id).update({
                    "cumulative_usage_times": charger.cumulative_usage_times,
                    "cumulative_charging_time": charger.cumulative_charging_time,
                    "cumulative_charging_amount": charger.cumulative_charging_amount
                })
                db.session.commit()
            success = True
            # 3.*******触发调度*******
            schedule(1, request.id)
            # 2.更新request状态
            db.session.query(ChargeRequest).filter(ChargeRequest.id == request.id).update({
                "state": 0
            })
            # remove
            db.session.query(WaitArea).filter(
                WaitArea.request_id == request.id).delete()
            db.session.query(WaitQueue).filter(
                WaitQueue.charge_id == request.charge_id).delete()
            db.session.query(ChargeArea).filter(
                ChargeArea.request_id == request.id).delete()
            db.session.query(ChargeWaitArea).filter(
                ChargeWaitArea.request_id == request.id).delete()
            db.session.commit()
        if success:
            record = db.session.query(ChargeRecord).filter(
                ChargeRecord.userId == user.id).order_by(ChargeRecord.id.desc()).first()
            return marshal(record,charge_record_fields)
        else:
            return {
                "code": -1,
                "message": error_msg
            }
class get_single_bill(Resource):
    @jwt_required()
    def get(self,billId):
        record=db.session.query(ChargeRecord).filter(ChargeRecord.id==billId).first()
        if record is None:
            return {
                "code": -1,
                "message": "未找到充电订单"
            }
        else:
            return marshal(record,charge_record_fields)
class get_bills(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, help='每页数量', default=-1, required=False,location='args')
        parser.add_argument('skip', type=int, help='偏移量', default=0, required=False,location='args')
        data = parser.parse_args()
        limit=data['limit']
        skip=data['skip']
        record_list = db.session.query(ChargeRecord).all()
        if len(record_list) == 0:
            return {
                "code": -1,
                "message": "未找到充电订单"
            }
        else:
            if limit==-1:
                return marshal(record_list[skip:],charge_record_fields)
            else:
                return marshal(record_list[skip:skip+limit], charge_record_fields)

class sys_time(Resource):
    def get(self):
        timer = Timer()
        return {
            "time": timer.get_cur_format_time()
        }
class sys_ping(Resource):
    def get(self):
        return {
            "code": 0,
            "message": "success"
        }


