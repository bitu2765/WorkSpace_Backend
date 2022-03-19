from flask import Blueprint,make_response,render_template,request,jsonify,Response
import hashlib
import datetime
from app import db
from models import Customer,Userlog,Admin,Adminlog
from userauth import user_auth,admin_auth

log = Blueprint('login',__name__)


@log.route('/logout',methods=['POST','GET'])
def logout_fun():
    user_token = request.cookies.get('auth_token')
    Userlog.query.filter_by(login_token = user_token).delete()
    Adminlog.query.filter_by(login_token = user_token).delete()
    db.session.commit()
    resp = make_response({"Msg":"Logout Succesfully"})
    resp.set_cookie("auth_id",'',expires=0)
    resp.set_cookie("auth_token",'',expires=0)
    return resp

@log.route('/login',methods=['POST'])
def login_fun():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.json
        # print(data)
        id=data['id']
        user=data['username']
        passwrd =data['password']
        response= {}
        Userlog.query.filter_by(customer_id = user).delete()
        Adminlog.query.filter_by(admin_email = user).delete()        
        if id == 1:
            exist = bool(db.session.query(Customer).filter_by(customer_id=user,password=passwrd,email_verify=True).first())
            if exist:
                token = "1"+user+passwrd+str(datetime.datetime.now())
                cnt=1
                us_token = bool(db.session.query(Userlog).filter_by(login_token=hashlib.sha512((token+str(cnt)).encode()).hexdigest()).first())
                while(us_token):
                    cnt+=1
                    us_token = bool(db.session.query(Userlog).filter_by(login_token=hashlib.sha512((token+str(cnt)).encode()).hexdigest()).first())
                response["Msg"] = "User Succesfully Logged In!" 
                response["auth_id"]=hashlib.sha512(("user"+user).encode()).hexdigest()
                response["auth_token"]=hashlib.sha512((token+str(cnt)).encode()).hexdigest()
                user_log = Userlog(customer_id=user,login_token=response['auth_token'])
                db.session.add(user_log)
                db.session.commit()
        # token = hashlib.sha512(token.encode()).hexdigest()
                resp = make_response(response)
                resp.set_cookie('auth_id', response["auth_id"],max_age=60*60*24*31)
                resp.set_cookie('auth_token', response["auth_token"],max_age=60*60*24*31)
                return resp
            else:
                exist = bool(db.session.query(Customer).filter_by(customer_id=user,password=passwrd,email_verify=False).first())
                if exist:
                    response["Msg"] = "Please Verify Email First "
                else:
                    response["Msg"] = "Incorrect Username or Password "
                return jsonify(response)
        elif id == 2:
            exist = bool(db.session.query(Admin).filter_by(admin_email=user,password=passwrd).first())
            if exist:
                response={}
                token = "2"+user+passwrd+str(datetime.datetime.now())
                cnt=1
                us_token = bool(db.session.query(Adminlog).filter_by(login_token=hashlib.sha512((token+str(cnt)).encode()).hexdigest()).first())
                while(us_token):
                    cnt+=1
                    us_token = bool(db.session.query(Adminlog).filter_by(login_token=hashlib.sha512((token+str(cnt)).encode()).hexdigest()).first())
                response["Msg"] = "User Succesfully Logged In!" 
                response["auth_id"]=hashlib.sha512(("admin"+user).encode()).hexdigest()
                response["auth_token"]=hashlib.sha512((token+str(cnt)).encode()).hexdigest()
                admin_log = Adminlog(admin_email=user,login_token=response['auth_token'])
                db.session.add(admin_log)
                db.session.commit()
                resp = make_response(response)
                resp.set_cookie('auth_id', response["auth_id"],max_age=60*60*24*31)
                resp.set_cookie('auth_token', response["auth_token"],max_age=60*60*24*31)
            else:
                response["Msg"] = "Incorrect Username or Password "
                return jsonify(response)
        else:
            response["Msg"]="Currently Admin Login not available"
        return jsonify(response)
    else:
        return jsonify({"Msg": "Content-Type not supported!"})
# print("hello")



@log.route('/user/verify',methods=['GET'])
@user_auth
def verify_user():
    resp = make_response({"success":1})
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

@log.route('/admin/verify', methods=['GET'])
@admin_auth
def admin_verify():
    return {
        "success":1
    }