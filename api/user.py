from flask import Blueprint,make_response,render_template,request
import uuid
import hashlib
from app import db,mail
from models import Customer, Plan_price, Purchase_hist, Location, Subscription_plan
from flask_mail import Mail, Message
from datetime import date
from sqlalchemy import and_
import json

user = Blueprint('user',__name__)


@user.route('/send_mail', methods=['GET'])
def send_mail():
    msg = Message(
        'Hello, From Motorola',
        sender='veetmoradiya7823@gmail.com',
        recipients=['bhautiksudani2765@gmail.com']
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return "Send Successfully"


@user.route('/user/register', methods=['POST'])
def temp_user_registration():
    # print(1)
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            data = request.json
            sender_uuid = uuid.uuid4()
            customer_id = data['customer_id']
            name = data['name']
            email = data['email']
            mobile_no = data['mobile_no']
            password = data['password']
            # print(name, email, mobile_no, password, sender_uuid)
            exist = bool(db.session.query(Customer).filter_by(email=email,
                                                              mobile_no=mobile_no,
                                                              customer_id=customer_id).first())
            if exist:
                return {"message": "Email already exists or mobile no "
                                   "is already exist or username already taken", "status_code": 404}
            else:
                user_data = Customer(sender_uuid=sender_uuid,
                                     customer_id=customer_id,
                                     name=name,
                                     email=email,
                                     mobile_no=mobile_no,
                                     password=password)
                db.session.add(user_data)
                db.session.commit()
                # mail code
                msg = Message(
                    'Hello, From ',
                    sender='veetmoradiya7823@gmail.com',
                    recipients=[email]
                )
                # obj = urlparse(request.base_url)
                verify_url = str('http://' + request.host + '/verify_user?token=' + str(sender_uuid))
                print(verify_url)
                msg.body = 'Hello User, please verify your self by clicking on this link \nLink : '+verify_url
                mail.send(msg)

                return {"message": "User Successfully registered. "
                                   "please verify your self link is send to your registered mail id.", "status_code": 200}
        else:
            return {"message": "Content-Type not supported!"}


@user.route('/verify_user', methods=['GET'])
def verify_user():
    tkn = str(request.args.get('token'))
    exist = bool(db.session.query(Customer).filter_by(token=tkn).first())
    print(exist)
    if exist:
        user_detail = Customer.query.filter_by(token=tkn).first()
        if user_detail.email_verify:
            return {"message":"User email already verified, please login now."}
        else:
            user_detail.email_verify = True
            db.session.commit()
            return {"message": "User with this token exists and verified", "status_code": 200}
    else:
        return {"message": "User with this token not exists. please register your self priorly", "status_code": 403}

@user.route("/user/<id>", methods=['GET'])
def user_profile(id):
    info = Customer.query.with_entities(Customer.name, Customer.email, Customer.mobile_no).filter_by(customer_id=id).first()
    if bool(info):
        return {
            "customer": {
                id: {
                    "name": info[0],
                    "email": info[1],
                    "mobile_no": info[2]
                }
            }
        }
    else:
        return{
            "message": "User: "+id+" doesn't exist."
        }

@user.route("/user/active_plan/<id>", methods=['GET'])
def active_plan(id):
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    info = Purchase_hist.query.join(
            Plan_price, Plan_price.plan_price_id == Purchase_hist.tbl_plan_price_id
        ).join(
            Location, Location.location_id == Plan_price.tbl_location_id
        ).join(
            Subscription_plan,Subscription_plan.plan_id == Plan_price.tbl_plan_id
        ).with_entities(
            Subscription_plan.capacity, Subscription_plan.duration, Purchase_hist.desk_no, Location.address, Location.city, 
            Location.state, Purchase_hist.price, Purchase_hist.end_date
        ).filter(
            and_(
                Purchase_hist.start_date <= today, Purchase_hist.end_date >= today, Purchase_hist.tbl_customer_id == id
            )
        ).all()

    if(bool(info)):
        json_list = []
        for i in range(0, len(info)):
            if info[i][0] == 1:
                plan_type = "Solo"
            elif info[i][0] == 2:
                plan_type = "Dual"
            elif info[i][0] == 4:
                plan_type = "Quad"
            
            end_date = info[i][7].strftime("%Y-%m-%d")
            value = {
                "plan_type": plan_type,
                "duration": info[i][1],
                "desk_no": info[i][2],
                "address": info[i][3],
                "city": info[i][4],
                "state": info[i][5],
                "price": info[i][6],
                "expiry_date": end_date
            }

            json_list.append(value)
        return json.dumps(json_list)
    else:
        return{
            "message": "No Active Plans of User: "+id+"."
        }

@user.route("/user/purchase_history/<id>", methods=['GET'])
def purchase_history(id):
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    info = Purchase_hist.query.join(
            Plan_price, Plan_price.plan_price_id == Purchase_hist.tbl_plan_price_id
        ).join(
            Location, Location.location_id == Plan_price.tbl_location_id
        ).join(
            Subscription_plan,Subscription_plan.plan_id == Plan_price.tbl_plan_id
        ).with_entities(
            Subscription_plan.capacity, Subscription_plan.duration, Purchase_hist.desk_no, Location.address, Location.city, 
            Location.state, Purchase_hist.price, Purchase_hist.start_date, Purchase_hist.end_date
        ).filter(Purchase_hist.tbl_customer_id == id).all()
    
    if(bool(info)):
        json_list = []
        for i in range(0, len(info)):
            if info[i][0] == 1:
                plan_type = "Solo"
            elif info[i][0] == 2:
                plan_type = "Dual"
            elif info[i][0] == 4:
                plan_type = "Quad"
            
            start_date = info[i][7].strftime("%Y-%m-%d")
            end_date = info[i][8].strftime("%Y-%m-%d")

            if start_date<=today and end_date>=today:
                plan_status = "Active"
            elif start_date>today and end_date>=today:
                plan_status = "Upcoming"
            elif end_date<today:
                plan_status = "Expired"

            value = {
                "plan_status": plan_status,
                "plan_type": plan_type,
                "duration": info[i][1],
                "desk_no": info[i][2],
                "address": info[i][3],
                "city": info[i][4],
                "state": info[i][5],
                "price": info[i][6],
                "start_date": start_date,
                "expiry_date": end_date
            }

            json_list.append(value)
        return json.dumps(json_list)
    else:
        return{
            "message": "User: "+id+" doesn't exist."
        }