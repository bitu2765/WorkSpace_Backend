from datetime import datetime, timedelta
from enum import auto
from app import db


# permanent user model
class Customer(db.Model):
    __tablename__ = 'tbl_customer'
    token = db.Column(db.String(100), unique=True)
    customer_id = db.Column(db.String(8), primary_key=True, unique=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mobile_no = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=False)
    email_verify = db.Column(db.Boolean, default=False)
    mobile_verify = db.Column(db.Boolean, default=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    block_user = db.Column(db.Boolean, default=False)

    def __init__(self, sender_uuid, customer_id, name, email, mobile_no, password):
        self.token = sender_uuid
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.mobile_no = mobile_no
        self.password = password
        self.email_verify = False
        self.mobile_verify = False
        self.registration_date = datetime.now()
        self.block_user = False


# location table
class Location(db.Model):
    __tablename__ = 'tbl_location'
    location_id = db.Column(db.String(5), primary_key=True, unique=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(30))
    state = db.Column(db.String(255))
    capacity = db.Column(db.Integer)
    # admins = db.relationship('Admin', backref='location')


# admin table
class Admin(db.Model):
    __tablename__ = 'tbl_admin'
    admin_email = db.Column(db.String(255), primary_key=True)
    admin_name = db.Column(db.String(30))
    password = db.Column(db.String(255))
    tbl_location_id = db.Column(db.String(5), db.ForeignKey('tbl_location.location_id'))


# subscription plans
class Subscription_plan(db.Model):
    __tablename__ = 'tbl_subscription_plan'
    plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    capacity = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    discount = db.Column(db.Float)
    __table_args__ = (db.UniqueConstraint('capacity', 'duration', name='capacity_duration_uc'),)


# plan price table
class Plan_price(db.Model):
    __tablename__ = 'tbl_plan_price'
    plan_price_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tbl_location_id = db.Column(db.String(5), db.ForeignKey('tbl_location.location_id'))
    tbl_plan_id = db.Column(db.Integer, db.ForeignKey('tbl_subscription_plan.plan_id'))
    price = db.Column(db.Integer)


# purchase history table
class Purchase_hist(db.Model):
    __tablename__ = 'tbl_purchase_history'
    # extra column
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tbl_customer_id = db.Column(db.String(8), db.ForeignKey('tbl_customer.customer_id'))
    tbl_plan_price_id = db.Column(db.Integer, db.ForeignKey('tbl_plan_price.plan_price_id'))
    desk_no = db.Column(db.Text)
    price = db.Column(db.Integer)
    purchase_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    payment_ref = db.Column(db.String(255))


# db.create_all()


class Userlog(db.Model):
    __tablename__ = 'tbl_user_log'
    login_token = db.Column(db.String(150), primary_key=True, unique=True, nullable=False)
    customer_id = db.Column(db.String(8), db.ForeignKey('tbl_customer.customer_id'), nullable=False)
    expiry_date = db.Column(db.DateTime)

    def __init__(self, login_token, customer_id):
        self.login_token = login_token
        self.customer_id = customer_id
        self.expiry_date = datetime.now() + timedelta(days=31)


class Adminlog(db.Model):
    __tablename__ = 'tbl_admin_log'
    login_token = db.Column(db.String(150), primary_key=True, unique=True, nullable=False)
    admin_email = db.Column(db.String(255), db.ForeignKey('tbl_admin.admin_email'), nullable=False)
    expiry_date = db.Column(db.DateTime)

    def __init__(self, login_token, admin_email):
        self.login_token = login_token
        self.admin_email = admin_email
        self.expiry_date = datetime.now() + timedelta(days=31)

    # db.create_all()

class BlockUserlog(db.Model):
    __tablename__ = 'tbl_block_user_log'
    block_user_log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tbl_customer_id = db.Column(db.String(8), db.ForeignKey('tbl_customer.customer_id'), nullable=False)
    mail_sent_date = db.Column(db.Date)
    mail_block_user = db.Column(db.Boolean, default=False)    
