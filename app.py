from flask import Flask,Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS


# CORS(app)

# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '7df7599fecf2a862f0699c1b86acfbde'

host = 'localhost'
user = 'root'
password = ''
database = 'moto_ps3_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + user + ':' + password + '@' + host + '/' + database


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'veetmoradiya7823@gmail.com'
app.config['MAIL_PASSWORD'] = 'veet@1234'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



db = SQLAlchemy(app)


# app.register_blueprint(test)
# bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'

# from flaskr import routes
# from models 
import models
#Customer,Location,Admin,Subscription_plan,Plan_price,Purchase_hist,Userlog

# class Customer(db.Model):
#     __tablename__ = 'tbl_customer'
#     token = db.Column(db.String(100), unique=True)
#     customer_id = db.Column(db.String(50), primary_key=True, unique=True)
#     name = db.Column(db.String(30), unique=False, nullable=False)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     mobile_no = db.Column(db.String(10), unique=True, nullable=False)
#     password = db.Column(db.String(255), unique=False, nullable=False)
#     email_verify = db.Column(db.Boolean, default=False)
#     mobile_verify = db.Column(db.Boolean, default=False)
#     registration_date = db.Column(db.DateTime, nullable=False)
#     block_user = db.Column(db.Boolean, default=False)

#     def __init__(self, sender_uuid, customer_id, name, email, mobile_no, password):
#         self.token = sender_uuid
#         self.customer_id = customer_id
#         self.name = name
#         self.email = email
#         self.mobile_no = mobile_no
#         self.password = password
#         self.email_verify = False
#         self.mobile_verify = False
#         self.registration_date = str(datetime.datetime.now())
#         self.block_user = False


db.create_all()
import routes

# from api.test import test

# app.register_blueprint(test)

if __name__ == "__main__":
    # db.create_all()
    
    app.run(host='192.168.43.123',port=5000)



















































