
HOSTNAME ='127.0.0.1'
PORT = 3306
USRNAME = 'root'
PASSWORD = 'lw181207'
DATABASE = 'test'
DB_URI = f'mysql+pymysql://{USRNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8'
SQLALCHEMY_DATABASE_URI = DB_URI

Charger_num = 5
wait_max_num=6
charge_max_num=3
fast_power=30
slow_power=10
status=['充电完成','等候区排队中','充电区等待中','充电中']
Charger_status = ['UNAVAILABLE','SHUTDOWN','RUNNING']
