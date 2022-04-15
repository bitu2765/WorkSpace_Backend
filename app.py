from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from flask_apscheduler import APScheduler

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '7df7599fecf2a862f0699c1b86acfbde'

host = 'localhost'
user = 'root'
password = ''
database = 'moto_ps3_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + user + ':' + password + '@' + host + '/' + database
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db = SQLAlchemy(app)

import models

db.create_all()

import routes
from api.admin import block_user

scheduler = APScheduler()
scheduler.add_job(id='BlockUser', func=block_user, trigger='interval', seconds=24 * 60 * 60)
scheduler.start()

if __name__ == "__main__":
    # db.create_all()
    app.run(host='192.168.43.123', port=5000)
