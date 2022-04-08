from unicodedata import name
from flask import Blueprint, make_response, render_template, request, g
import uuid
import hashlib
from app import db, mail
from models import Customer, Plan_price, Purchase_hist, Location, Subscription_plan
from flask_mail import Mail, Message
from datetime import date,datetime, timedelta
from sqlalchemy import and_
import json
import math
from dateutil import parser
from userauth import user_auth
import re
import logging

user = Blueprint('user', __name__)

# logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler = logging.FileHandler('logs/user_registration.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@user.route('/mail_template_render', methods = ['GET'])
def mail_render():
    return render_template('/mails/mail.html')

# temporart mail api 
@user.route('/send_mail', methods=['GET'])
def send_mail():
    msg = Message(
        'Hello, From Motorola',
        sender='veetmoradiya7823@gmail.com',
        recipients=['19it069@charusat.edu.in']
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    username = "Moradiya Veet"
    link = "http://localhost:5000/verify_user"
    msg.html = render_template('/mails/mail.html', name=username, link=link)
    mail.send(msg)
    return "Send Successfully"


@user.route('/user/register', methods=['POST'])
def temp_user_registration():
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

            # user details validation
            # email validation
            email_valid = mobile_valid = password_valid = False

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.match(regex, email):
                email_valid = True
            # mobile no. validation
            if len(str(mobile_no)) == 10:
                mobile_valid = True

            # password validation
            if 8 <= len(password) <= 32:
                password_valid = True

            if not password_valid:
                return {"message": "password must be between 8 to 32 words.", "status_code": 404}
            elif not email_valid:
                return {"message": "email is not valid", "status_code": 404}
            elif not mobile_valid:
                return {"message": "mobile number is not valid.", "status_code": 404}
            else:
                exist_customer_id = bool(db.session.query(Customer).filter_by(customer_id=customer_id).all())
                exist_email = bool(db.session.query(Customer).filter_by(email=email).all())
                exist_mobile = bool(db.session.query(Customer).filter_by(mobile_no=mobile_no).all())

                if exist_customer_id:
                    return {"message": "user id already taken", "status_code": 404}
                elif exist_email:
                    return {"message": "email already taken. please try another email id.", "status_code": 404}
                elif exist_mobile:
                    return {"message": "mobile number already taken. please try another mobile number.",
                            "status_code": 404}
                else:
                    user_data = Customer(sender_uuid=sender_uuid,
                                         customer_id=customer_id,
                                         name=name,
                                         email=email,
                                         mobile_no=mobile_no,
                                         password=password)
                    db.session.add(user_data)
                    db.session.commit()
                    # log
                    logger.info('New User created with username : {0}'.format(customer_id))
                    # mail code
                    msg = Message(
                        'WorkSpace - Registration Confirmation',
                        sender='veetmoradiya7823@gmail.com',
                        recipients=[email]
                    )
                    # obj = urlparse(request.base_url)
                    verify_url = str('http://' + request.host + '/verify_user?token=' + str(sender_uuid))
                    print(verify_url)
                    username = customer_id
                    msg.html = render_template('/mails/registration_mail.html', name=username, link=verify_url)
                    mail.send(msg)
                    # log
                    logger.info('Mail is send to user : {0} with link as : {1}'.format(customer_id, verify_url))
                    return {"message": "User Successfully registered. "
                                       "please verify your self link is send to your registered mail id.",
                            "status_code": 200}
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
            return {"message": "User email already verified, please login now."}
        else:
            user_detail.email_verify = True
            db.session.commit()
            # log
            logger.info('User verified with token {0}'.format(tkn))
            return {"message": "User with this token exists and verified", "status_code": 200}
    else:
        return {"message": "User with this token not exists. please register your self priorly", "status_code": 403}


@user.route("/user/profile", methods=['GET'])
@user_auth
def user_profile():
    info = Customer.query.with_entities(Customer.name, Customer.email, Customer.mobile_no).filter_by(
        customer_id=g.token).first()
    if bool(info):
        resp = make_response(
            {
                "status_code": 200,
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
                "status_code": 404,
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
        Subscription_plan, Subscription_plan.plan_id == Plan_price.tbl_plan_id
    ).with_entities(
        Subscription_plan.capacity, Subscription_plan.duration, Purchase_hist.desk_no, Location.address, Location.city,
        Location.state, Purchase_hist.price, Purchase_hist.end_date
    ).filter(
        and_(
            Purchase_hist.start_date <= today, Purchase_hist.end_date >= today, Purchase_hist.tbl_customer_id == g.token
        )
    ).order_by(Purchase_hist.end_date).all()

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
                "desk_no": info[i][2].split(','),
                "address": info[i][3],
                "city": info[i][4],
                "state": info[i][5],
                "price": info[i][6],
                "expiry_date": end_date
            }
            json_list.append(value)

        resp = make_response({
            "status_code": 200,
            "active_plans": json_list
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response({
            "status_code": 404,
            "message": "No Active Plans."
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp


@user.route("/user/upcoming_plan", methods=['GET'])
@user_auth
def upcoming_plan():
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    info = Purchase_hist.query.join(
        Plan_price, Plan_price.plan_price_id == Purchase_hist.tbl_plan_price_id
    ).join(
        Location, Location.location_id == Plan_price.tbl_location_id
    ).join(
        Subscription_plan, Subscription_plan.plan_id == Plan_price.tbl_plan_id
    ).with_entities(
        Subscription_plan.capacity, Subscription_plan.duration, Purchase_hist.desk_no, Location.address, Location.city,
        Location.state, Purchase_hist.price, Purchase_hist.start_date
    ).filter(
        and_(
            Purchase_hist.start_date > today, Purchase_hist.end_date >= today, Purchase_hist.tbl_customer_id == g.token
        )
    ).order_by(Purchase_hist.start_date).all()

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
            value = {
                "plan_type": plan_type,
                "duration": info[i][1],
                "desk_no": info[i][2].split(','),
                "address": info[i][3],
                "city": info[i][4],
                "state": info[i][5],
                "price": info[i][6],
                "start_date": start_date
            }
            json_list.append(value)

        resp = make_response({
            "status_code": 200,
            "upcoming_plans": json_list
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response({
            "status_code": 404,
            "message": "No Upcoming Plans."
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp


@user.route("/user/purchase_plan", methods=['POST'])
@user_auth
def purchase_plan():
    # print(1)
    errors = []
    is_error = False

    # if request.method == 'POST':
    #     content_type = request.headers.get('Content-Type')
    #     if content_type == 'application/json':
    data = request.json
    plan_id = data['plan_id']
    location_id = data['location_id']
    start_date = data['start_date']

    start_date = parser.parse(start_date)
    if start_date.strftime("%Y-%m-%d") < date.today().strftime("%Y-%m-%d"):
        resp1 = make_response({
            "status_code": 422,
            "message": "Plan Starting Date must be on or after " + date.today().strftime("%Y-%m-%d") + "."
        })
        resp1.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp1

    valid_plan_id = Subscription_plan.query.filter_by(plan_id=plan_id).all()
    if not (bool(valid_plan_id)):
        is_error = True
        errors.append("Plan id doesn't exist.")

    valid_user_id = Customer.query.filter_by(customer_id=g.token).all()
    if not (bool(valid_user_id)):
        is_error = True
        errors.append("User id doesn't exist.")

    valid_location_id = Location.query.filter_by(location_id=location_id).all()
    if not (bool(valid_location_id)):
        is_error = True
        errors.append("Location id doesn't exist.")

    if is_error:
        resp2 = make_response({
            "status_code": 404,
            "errors": errors
        })
        resp2.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp2
    plan_price_id = Plan_price.query.with_entities(Plan_price.plan_price_id).filter(
        Plan_price.tbl_location_id == location_id).all()

    alloted_desk_no = []
    for i in range(0, len(plan_price_id)):
        deskno = Purchase_hist.query.with_entities(Purchase_hist.desk_no).filter(
            and_(Purchase_hist.tbl_plan_price_id == plan_price_id[i][0], Purchase_hist.end_date > start_date)).all()
        if bool(deskno):
            for j in range(0, len(deskno)):
                alloted_desk_no.append(list(map(int, deskno[j][0].split(','))))
        else:
            continue

    final_alloted_desk_no = []
    for i in range(0, len(alloted_desk_no)):
        for j in range(0, len(alloted_desk_no[i])):
            final_alloted_desk_no.append(alloted_desk_no[i][j])

    capacity = Location.query.with_entities(Location.capacity).filter(
        Location.location_id == location_id).first()
    desk_slots = {}
    for i in range(1, capacity[0] + 1):
        desk_slots[i] = True

    for i in range(0, len(final_alloted_desk_no)):
        desk_slots[final_alloted_desk_no[i]] = False

    avail_slots = []
    for key, val in desk_slots.items():
        if val == True:
            avail_slots.append(key)
    required_desk_slots = Subscription_plan.query.with_entities(Subscription_plan.capacity).filter(
        Subscription_plan.plan_id == plan_id).first()

    if required_desk_slots[0] > len(avail_slots):
        resp3 = make_response({
            "status_code": 404,
            "message": "No more Available Desks. Hoping for serving you better Next Time."
        })
        resp3.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp3

    allotment = []
    for i in range(0, required_desk_slots[0]):
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
    price = price_discount_duration[0] - ((price_discount_duration[0] * price_discount_duration[1]) / 100)
    price = int(math.ceil(price))

    purchase_date = date.today().strftime("%Y-%m-%d")

    end_date = start_date + timedelta(days=price_discount_duration[2])
    end_date = end_date.strftime("%Y-%m-%d")

    get_plan_price_id = Plan_price.query.with_entities(Plan_price.plan_price_id).filter(
        and_(Plan_price.tbl_location_id == location_id, Plan_price.tbl_plan_id == plan_id)
    ).first()

    purchase_history = Purchase_hist(
        tbl_customer_id=g.token,
        tbl_plan_price_id=get_plan_price_id[0],
        desk_no=desk_no,
        price=price,
        purchase_date=purchase_date,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(purchase_history)
    db.session.commit()

    resp = make_response({
        "status_code": 200,
        "message": "Plan purchased Successfully."
    })
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp
    # else:
    #     resp = make_response({
    #         "status_code": 415,
    #         "message": "Content-Type not supported!"
    #     })
    #     resp.headers['Access-Control-Allow-Credentials'] = 'true'
    #     return resp


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
        Subscription_plan, Subscription_plan.plan_id == Plan_price.tbl_plan_id
    ).with_entities(
        Subscription_plan.capacity, Subscription_plan.duration, Purchase_hist.desk_no, Location.address, Location.city,
        Location.state, Purchase_hist.price, Purchase_hist.purchase_date, Purchase_hist.start_date,
        Purchase_hist.end_date
    ).order_by(Purchase_hist.purchase_date.desc()).filter(Purchase_hist.tbl_customer_id == g.token).all()

    if bool(info):
        json_list = []
        for i in range(0, len(info)):
            if info[i][0] == 1:
                plan_type = "Solo"
            elif info[i][0] == 2:
                plan_type = "Dual"
            elif info[i][0] == 4:
                plan_type = "Quad"

            purchase_date = info[i][7].strftime("%Y-%m-%d")
            start_date = info[i][8].strftime("%Y-%m-%d")
            end_date = info[i][9].strftime("%Y-%m-%d")

            if start_date <= today and end_date >= today:
                plan_status = "Active"
            elif start_date > today and end_date >= today:
                plan_status = "Upcoming"
            elif end_date < today:
                plan_status = "Expired"

            value = {
                "plan_status": plan_status,
                "plan_type": plan_type,
                "duration": info[i][1],
                "desk_no": info[i][2].split(','),
                "address": info[i][3],
                "city": info[i][4],
                "state": info[i][5],
                "price": info[i][6],
                "purchase_date": purchase_date,
                "start_date": start_date,
                "expiry_date": end_date
            }

            json_list.append(value)

        resp = make_response({
            "status_code": 200,
            "purchase_history": json_list
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response({
            "status_code": 404,
            "message": "User doesn't exist."
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp


@user.route('/user/desk_details', methods=["GET"])
@user_auth
def user_desk_details():
    # data = request.args
    # print(data)
    search_date = request.args.get("date")
    location_id = request.args.get('location')
    # print(search_date)
    if search_date=="":
        search_date = datetime.now()
    valid_location_id = Location.query.filter_by(location_id=location_id).all()
    if not (bool(valid_location_id)):
        resp = make_response(
            {
                "status_code": 401,
                "message": "location not exist"
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    location = db.session.query(Location).with_entities(
        Location.capacity
    ).filter(
        Location.location_id == location_id
    ).first()

    desk_details = db.session.query(Plan_price, Purchase_hist).with_entities(
        Purchase_hist.desk_no
    ).filter(
        Plan_price.tbl_location_id == location_id, Purchase_hist.tbl_plan_price_id == Plan_price.plan_price_id,
        Purchase_hist.start_date <= search_date, Purchase_hist.end_date >= search_date
    ).all()
    # print(search_date)

    desk_detail_list = [0 for i in range(location['capacity'])]

    for i in desk_details:
        for j in i['desk_no'].split(","):
            # print(j)
            desk_detail_list[int(j) - 1] = 1

    resp = make_response(
        {
            "status_code": 200,
            "desks": desk_detail_list,
            # "date":date,
            "message": "No one have purchase any plan"
        }
    )
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


