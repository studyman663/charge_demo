from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

def print_hello():
    print("hello")

scheduler.add_job(func=print_hello, trigger='interval', seconds=1)
scheduler.start()

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()