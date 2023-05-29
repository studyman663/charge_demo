from sqlalchemy.orm import sessionmaker


from passlib.hash import pbkdf2_sha256 as sha256
from config import *
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), User.query.all()))}
    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class Charger(db.Model): #充电桩信息
    __tablename__ = 'charger'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    charger_status = db.Column(db.Enum('RUNNING', 'SHUTDOWN', 'UNAVAILABLE'),default='RUNNING')
    type = db.Column(db.String(20))
    ChargingQueueLen = db.Column(db.Integer,default=charge_max_num)  # 充电桩排队队列长度
    last_end_time = db.Column(db.BIGINT)  # 当前充电桩充电区最后一辆车预计充电结束时间
    cumulative_usage_times = db.Column(db.Integer, default=0)  # 充电桩累计使用次数
    cumulative_charging_time = db.Column(db.Integer, default=0)  # 充电桩累计充电时间
    cumulative_charging_amount = db.Column(db.String(20), default="0")  # 充电桩累计充电电量
    start_time = db.Column(db.BIGINT, default=0)  # 充电桩的启动时间
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class ChargeArea(db.Model): #每个充电桩的充电区内正在充电和正在等待的充电请求号
    __tablename__ = 'charge_area'
    pile_id = db.Column(db.String(20))  # 充电桩号
    request_id = db.Column(db.String(20), primary_key=True)
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class ChargeWaitArea(db.Model):
    __tablename__ = 'charge_wait_area'
    type = db.Column(db.String(20))  # F/T
    request_id = db.Column(db.String(20), primary_key=True)
    WaitingAreaSize = db.Column(db.Integer,default=wait_max_num)  # 等候区车位容量
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class WaitArea(db.Model):
    __tablename__ = 'wait_area'
    type = db.Column(db.String(20))  # F/T
    request_id = db.Column(db.String(20), primary_key=True)
    WaitingAreaSize = db.Column(db.Integer,default=wait_max_num)  # 等候区车位容量
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class ChargeRecord(db.Model):
    __tablename__ = 'charge_record'
    id = db.Column(db.String(20), primary_key=True)  # 编号
    order_id = db.Column(db.String(20))  # 订单号
    created_at = db.Column(db.String(20))  # 详单生成时间
    chargeAmount = db.Column(db.Float)  # 充电电量
    charged_time = db.Column(db.Integer)  # 充电时长
    chargeStartTime = db.Column(db.String(20))  # 开始充电时间
    chargeEndTime = db.Column(db.String(20))  # 结束时间
    deleted_at=db.Column(db.String(20),default='null')  # 删除时间
    updated_at=db.Column(db.String(20))  # 更新时间
    chargeFee = db.Column(db.Float)  # 充电费用
    serviceFee = db.Column(db.Float)  # 服务费用
    totalFee = db.Column(db.Float)  # 总费用
    pileId = db.Column(db.String(20))  # 充电桩号
    userId = db.Column(db.String(20))  # 用户id
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class ChargeRequest(db.Model):
    __tablename__ = 'charge_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    # 0代表不在充电，1代表在等候区等待，2代表充电区等待，3代表正在充电，4表示充电模式更改导致的重新排队，5表示充电桩故障需要转移充电桩
    state = db.Column(db.Integer, default=0)
    user_id = db.Column(db.String(20))
    charge_mode = db.Column(db.String(20))
    require_amount = db.Column(db.Float)  # 充电量
    charge_time = db.Column(db.Float)  # 充电所需时间：充电量除以功率 单位：s
    start_time = db.Column(db.BIGINT)  # 开始充电时间
    battery_size = db.Column(db.Float)  # 电池电量大小
    charge_id = db.Column(db.String(20))  # 等候区排队号
    charge_pile_id = db.Column(db.String(20))  # 充电桩编号
    request_submit_time = db.Column(db.BIGINT)  # 充电请求提交时间
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class WaitQueue(db.Model):
    __tablename__ = 'wait_queue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum('F', 'T'))
    state = db.Column(db.Integer)  # 0代表排队号无效，1代表排队号有效（即在排队队列中）
    charge_id = db.Column(db.String(20))  # 等候区排队号
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


