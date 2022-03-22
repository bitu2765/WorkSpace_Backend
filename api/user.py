from flask import Blueprint,make_response,render_template,request,g
import uuid
import hashlib
from app import db,mail
from models import Customer, Plan_price, Purchase_hist, Location, Subscription_plan
from flask_mail import Mail, Message
from datetime import date, timedelta
from sqlalchemy import and_
import json
import math
from dateutil import parser
from userauth import user_auth

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

@user.route("/user/profile", methods=['GET'])
@user_auth
def user_profile():
    info = Customer.query.with_entities(Customer.name, Customer.email, Customer.mobile_no).filter_by(customer_id=g.token).first()
    if bool(info):
        resp = make_response(
            {
                "status_code":200,
                "customer": {
                    "name": info[0],
                    "email": info[1],
                    "mobile_no": info[2]
                }
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code":404,
                "message": "User doesn't exist."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

@user.route("/user/active_plan", methods=['GET'])
@user_auth
def active_plan():
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
                Purchase_hist.start_date <= today, Purchase_hist.end_date >= today, Purchase_hist.tbl_customer_id == g.token
            )
        ).all()

    if bool(info):
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
        
        resp = make_response({
            "status_code": 200,
            "active_plans":json.dumps(json_list)
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response({
            "status_code":404,
            "message": "No Active Plans."
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

@user.route("/user/purchase_plan", methods=['POST'])
@user_auth
def purchase_plan():
    errors = []
    is_error = False

    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            data = request.json
            plan_id = data['plan_id']
            location_id = data['location_id']
            start_date = data['start_date']

            start_date = parser.parse(start_date)
            if start_date.strftime("%Y-%m-%d")<date.today().strftime("%Y-%m-%d"):
                resp1 = make_response({
                    "status_code": 422,
                    "message": "Plan Starting Date must be on or after "+ date.today().strftime("%Y-%m-%d") +"."
                })
                resp1.headers['Access-Control-Allow-Credentials'] = 'true'
                return resp1
            
            valid_plan_id = Subscription_plan.query.filter_by(plan_id=plan_id).all()
            if not(bool(valid_plan_id)):
                is_error = True
                errors.append("Plan id doesn't exist.")
            
            valid_user_id = Customer.query.filter_by(customer_id=g.token).all()
            if not(bool(valid_user_id)):
                is_error = True
                errors.append("User id doesn't exist.")
            
            valid_location_id = Location.query.filter_by(location_id=location_id).all()
            if not(bool(valid_location_id)):
                is_error = True
                errors.append("Location id doesn't exist.")
            
            if is_error:
                resp2 = make_response({
                    "status_code": 404,
                    "errors": errors
                })
                resp2.headers['Access-Control-Allow-Credentials'] = 'true'
                return resp2
            
            plan_price_id = Plan_price.query.with_entities(Plan_price.plan_price_id).filter(Plan_price.tbl_location_id == location_id).all()
            
            alloted_desk_no = []
            for i in range(0, len(plan_price_id)):
                deskno = Purchase_hist.query.with_entities(Purchase_hist.desk_no).filter(Purchase_hist.tbl_plan_price_id == plan_price_id[i][0]).all()
                if bool(deskno):
                    for j in range(0,len(deskno)):
                        alloted_desk_no.append(list(map(int,deskno[j][0].split(','))))
                else:
                    continue

            final_alloted_desk_no = []
            for i in range(0,len(alloted_desk_no)):
                for j in range(0,len(alloted_desk_no[i])):
                    final_alloted_desk_no.append(alloted_desk_no[i][j])

            capacity = Location.query.with_entities(Location.capacity).filter(Location.location_id == location_id).first()
            desk_slots={}
            for i in range(1,capacity[0]+1):
                desk_slots[i] = True

            for i in range(0,len(final_alloted_desk_no)):
                desk_slots[final_alloted_desk_no[i]] = False
            
            avail_slots = []
            for key,val in desk_slots.items():
                if val == True:
                    avail_slots.append(key)
            required_desk_slots = Subscription_plan.query.with_entities(Subscription_plan.capacity).filter(Subscription_plan.plan_id == plan_id).first()

            if required_desk_slots[0]>len(avail_slots):
                resp3 = make_response({
                    "status_code": 404,
                    "message": "No more Available Desks. Hoping for serving you better Next Time."
                })
                resp3.headers['Access-Control-Allow-Credentials'] = 'true'
                return resp3
            
            allotment = []
            for i in range(0,required_desk_slots[0]):
                allotment.append(avail_slots[i])
                desk_slots[allotment[i]] = False

            desk_no = ''
            for i in range(len(allotment)):
                desk_no = desk_no + ',' + str(allotment[i])
            desk_no = desk_no[1:]

            price_discount_duration = Subscription_plan.query.join(
                    Plan_price, Subscription_plan.plan_id == Plan_price.tbl_plan_id
                ).with_entities(
                    Plan_price.price, Subscription_plan.discount, Subscription_plan.duration
                ).filter(Subscription_plan.plan_id == plan_id).first()
            price = price_discount_duration[0]-((price_discount_duration[0]*price_discount_duration[1])/100)
            price = int(math.ceil(price))

            purchase_date = date.today().strftime("%Y-%m-%d")

            end_date =  start_date + timedelta(days=price_discount_duration[2])
            end_date = end_date.strftime("%Y-%m-%d") 

            purchase_history = Purchase_hist(
                tbl_customer_id = g.token,
                tbl_plan_price_id = plan_id,
                desk_no = desk_no,
                price = price,
                purchase_date = purchase_date,
                start_date = start_date,
                end_date = end_date
            )
            db.session.add(purchase_history)
            db.session.commit()

            resp = make_response({
                "status_code": 200,
                "message": "Plan purchased Successfully."
            })
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
            return resp
        else:
            resp = make_response({
                "status_code": 415,
                "message": "Content-Type not supported!" 
            })
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
            return resp

@user.route("/user/purchase_history", methods=['GET'])
@user_auth
def purchase_history():
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
        ).filter(Purchase_hist.tbl_customer_id == g.token).all()
    
    if bool(info):
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
        
        resp = make_response({
            "status_code": 200,
            "purchase_history": json.dumps(json_list)
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response({
            "status_code":404,
            "message": "User doesn't exist."
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp