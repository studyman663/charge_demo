
HOSTNAME ='127.0.0.1'
PORT = 3306
USRNAME = 'root'
PASSWORD = 'lw181207'
DATABASE = 'test'
DB_URI = f'mysql+pymysql://{USRNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8'
SQLALCHEMY_DATABASE_URI = DB_URI

Charger_num = 5
wait_max_num=6
charge_max_num=2
fast_power=30
slow_power=7
print_time=10*3 #定时打印各充电桩当前队列状态以及等候区状态，间隔分钟*3秒
status=['充电完成','等候区排队中','充电区等候中','充电中']
Charger_status = ['UNAVAILABLE','SHUTDOWN','RUNNING']
