from functools import wraps
import datetime
from flask import request,Response,redirect,url_for,g,make_response
import hashlib
from models import Userlog,Adminlog
from app import db


def user_auth(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        user_token = request.cookies.get('auth_token')
        user_id = request.cookies.get('auth_id')
        token="token-123"
        log_exist = bool(db.session.query(Userlog).filter_by(login_token=user_token).first())
        # datetime.datetime.now()#datetime.datetime.strptime(str(user_detail['expiry_date']), '%yyyy-%mm-%dd %HH:%MM:%SS')
        # print(log_exist)
        # print(date>datetime.datetime.now())
        # id = hashlib.sha512(("user"+user_detail['customer_id']).encode()).hexdigest()
        if log_exist:
            user_detail = db.session.query(Userlog.customer_id,Userlog.expiry_date).filter_by(login_token=user_token).first()
            # id = 1
            # print(user_detail)
            date = user_detail['expiry_date']
            if hashlib.sha512(("user"+user_detail['customer_id']).encode()).hexdigest() == user_id:
                if date>datetime.datetime.now() :
                    g.token=user_detail['customer_id']
                    g.id = 1
                    return f(*args,**kwargs)

        resp = make_response({"status_code":404})
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
        # return Response("Authorization Failed!!")

    return decorated_function



def admin_auth(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        user_token = request.cookies.get('auth_token')
        user_id = request.cookies.get('auth_id')
        token="token-123"
        log_exist = bool(db.session.query(Adminlog).filter_by(login_token=user_token).first())
        # datetime.datetime.now()#datetime.datetime.strptime(str(user_detail['expiry_date']), '%yyyy-%mm-%dd %HH:%MM:%SS')
        # print(datetime.datetime.now())
        # print(date>datetime.datetime.now())
        # id = hashlib.sha512(("user"+user_detail['customer_id']).encode()).hexdigest()
        if log_exist:
            user_detail = db.session.query(Adminlog.admin_email,Adminlog.expiry_date).filter_by(login_token=user_token).first()
            # id = 1
            # print(user_detail)
            date = user_detail['expiry_date']
            if hashlib.sha512(("admin"+user_detail['admin_email']).encode()).hexdigest() == user_id:
                if date>datetime.datetime.now() :
                    g.token=user_detail['admin_email']
                    g.id = 2
                    return f(*args,**kwargs)

        resp = make_response({"status_code":404})
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
        # return Response("Authorization Failed!!")

    return decorated_function

