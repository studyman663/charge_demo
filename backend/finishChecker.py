import datetime
import json
import os

from sqlalchemy import and_

from app import db
from config import fast_power, slow_power
from models import ChargeRequest, ChargeRecord, Charger, WaitArea, WaitQueue, ChargeArea, ChargeWaitArea, User
from Timer import Timer
from schedule import schedule


def check_finish():
    timer = Timer()
    to_check = db.session.query(ChargeRequest).filter(ChargeRequest.state == 3).all()
    for charge_request in to_check:
        if charge_request.start_time + charge_request.charge_time <= timer.get_cur_timestamp():
            end_charging_request(db.session.query(User).filter(User.id == charge_request.user_id).first(),
                                 charge_request.start_time + charge_request.charge_time)
            print("finish checker: end charging request " + str(charge_request.id))
        else:
            update_charging_request(charge_request, timer.get_cur_timestamp())


def update_charging_request(request, cur_time):
    timer = Timer()
    end_time = datetime.datetime.fromtimestamp(cur_time)
    begin_time = datetime.datetime.fromtimestamp(request.start_time)
    charged_time = (end_time - begin_time).seconds  # 充电时长
    if request.charge_mode == 'F':
        rate = fast_power
    else:
        rate = slow_power
    cur_amount = (charged_time / 3600) * rate
    service_cost = float('%0.2f' % (0.8 * float(cur_amount)))  # 服务费用
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
                cur_amount * fees[begin_time_zone - 1]))  # 充电费用
    else:
        # 分别计算开始时间到临界值的时间，结束时间到临界值的时间。单位为秒
        diff_time1 = (clocks[begin_time_zone] - (
            begin_time.hour if begin_time.hour >= 7 else (begin_time.hour + 24)) - 1) * 3600 + \
                     (60 - begin_time.minute) * \
                     60 + 60 - begin_time.second
        diff_time2 = ((end_time.hour if begin_time.hour >= 7 else (begin_time.hour + 24)) - clocks[
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
    db.session.query(ChargeRequest).filter(ChargeRequest.id == request.id).update({
        "currentAmount": cur_amount,
        "currentFee": total_cost
    })
    db.session.commit()


def end_charging_request(user, end_time):
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
        now = datetime.datetime.fromtimestamp(end_time)
        # "order_id": "20220101000001",
        order_id = now.strftime("%Y%m%d") + '%06d' % request.id
        record_id = str(db.session.query(ChargeRecord).count() + 1)
        # 如果当前正在充电，计算后再创建充电详单 question：算法尚未测试
        begin_time = datetime.datetime.fromtimestamp(request.start_time)
        end_time = now
        charged_time = (end_time - begin_time).seconds  # 充电时长
        if request.charge_mode == "F":
            rate = fast_power
        else:
            rate = slow_power
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
                                     totalFee=total_cost, pileId=request.charge_pile_id, userId=user.id,
                                     updated_at=create_time
                                     )
        db.session.add(charge_record)
        db.session.commit()
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
        # 3.*******触发调度*******
        schedule(1, request.id)
        # 2.更新request状态
        db.session.query(ChargeRequest).filter(ChargeRequest.id == request.id).update({
            "state": 0,
            "currentAmount": request.require_amount,
            "currentFee": total_cost
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
    return


def print_result():
    # pass
    timer=Timer()
    chargelist = []
    waitlist = []
    pile_list = db.session.query(Charger).all()
    for pile in pile_list:
        c_request = db.session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == pile.id).all()
        print(timer.get_cur_format_time(),len(c_request))
        if len(c_request) != 0:
            for tmp in c_request:
                request = db.session.query(ChargeRequest).filter(ChargeRequest.id == int(tmp[0])).first()
                name = db.session.query(User.username).filter(User.id == request.user_id).first()[0]
                chargelist.append((pile.id,name,round(request.currentAmount, 2),round(request.currentFee, 2)))
    wait_list = db.session.query(WaitArea).all()
    if len(wait_list) !=0:
        for wait in wait_list:
            request = db.session.query(ChargeRequest).filter(ChargeRequest.id == wait.request_id).first()
            name = db.session.query(User.username).filter(User.id == request.user_id).first()[0]
            waitlist.append((name,request.charge_mode,round(request.require_amount, 2)))
    chargelist_file = 'chargelist.txt'
    waitlist_file = 'waitlist.txt'
    with open(chargelist_file, 'a') as f:
        f.write(f'{timer.get_cur_format_time()}: ')
        for charge in chargelist:
            f.write(str(charge))
        f.write('\n')
    with open(waitlist_file, 'a') as f:
        f.write(f'{timer.get_cur_format_time()}: ')
        for wait in waitlist:
            f.write(str(wait))
        f.write('\n')
