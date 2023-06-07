import datetime
import time


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class Timer(object):
    flag_time=datetime.datetime.now()
    start_time = datetime.datetime(2023, 6, 6, 5, 58, 0)
    speed = 20
    def __init__(self):
        pass
    def get_cur_timestamp(self):
        return int((datetime.datetime.now().timestamp() - self.flag_time.timestamp()) * self.speed + self.start_time.timestamp())

    def get_cur_format_time(self):
        return datetime.datetime.fromtimestamp(int((datetime.datetime.now().timestamp() - self.flag_time.timestamp()) * self.speed + self.start_time.timestamp() )).strftime('%Y-%m-%d %H:%M:%S')


# if __name__ == '__main__':
#     timer = Timer()
#     print(timer.get_cur_timestamp())
#     print(timer.get_cur_format_time())
#     time.sleep(2)
#     print(timer.get_cur_timestamp())
#     print(timer.get_cur_format_time())
