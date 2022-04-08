from flask import Blueprint, make_response, render_template, request, g
from app import db
from models import Admin, BlockUserlog, Customer, Location, Purchase_hist,Plan_price, Subscription_plan
from userauth import admin_auth
from datetime import date
from sqlalchemy import and_
from api.user import user_desk_details

admin = Blueprint('admin', __name__)


@admin.route('/admin/profile', methods=['GET'])
@admin_auth
def admin_profile():
    info = Admin.query.join(
        Location, Admin.tbl_location_id == Location.location_id
    ).with_entities(
        Admin.admin_email, Admin.admin_name, Location.address, Location.city, Location.state
    ).filter(Admin.admin_email == g.token).first()

    if bool(info):
        resp = make_response({
            "status_code": 200,
            "admin": {
                "email": info[0],
                "name": info[1],
                "address": info[2],
                "city": info[3],
                "state": info[4]
            }
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code": 404,
                "message": "Admin doesn't exist."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp


# all users details for admin side to show list of users
@admin.route('/admin/user_details', methods=['GET'])
@admin_auth
def users_details():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    users = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    user_list = []

    for user in users.items:
        _user = {
            "name": user.name,
            "email": user.email,
            "email_verified": user.email_verify,
            "is_block": user.block_user
        }
        user_list.append(_user)

    meta = {
        "page": users.page,
        "pages": users.pages,
        "total_count": users.total,
        "prev_page": users.prev_num,
        "next_page": users.next_num,
        "has_next": users.has_next,
        "has_prev": users.has_prev,
    }

    resp = make_response({
        "status_code": "200",
        "paginate": meta,
        "customers": user_list
    })
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


# all user purchase plan history

@admin.route('/admin/user_purchase_plan_details',methods = ["GET"])
@admin_auth
def user_details():
    userInfo = db.session.query(Customer, Purchase_hist).filter(
        Customer.customer_id == Purchase_hist.tbl_customer_id).all()

    if bool(userInfo):

        records = []
        name = desk_no = price = purchase_date = start_date = end_date = None

        for c, p in db.session.query(Customer, Purchase_hist).filter(
                Customer.customer_id == Purchase_hist.tbl_customer_id).all():
            name = c.name
            desk_no = p.desk_no
            price = p.price
            purchase_date = p.purchase_date
            start_date = p.start_date
            end_date = p.end_date

            obj = {
                'Name': name,
                'Desk no.': desk_no,
                'Plan price': price,
                'Purchase date': purchase_date,
                'Start date': start_date,
                'End date': end_date
            }

            records.append(obj)

        resp = make_response(
            {
                "status_code": 200,
                "user_purchsed_plans_details": records
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code": 404,
                "message": "No one have purchase any plan"
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

def block_user():
    list_unblock_user = Customer.query.with_entities(Customer.customer_id).filter_by(block_user=0).all()
    today = date.today()
    if bool(list_unblock_user):
        list_user = []
        for i in range(0, len(list_unblock_user)):
            list_user.append(list_unblock_user[i][0])

        for i in range(0, len(list_user)):
            purchase_history = Purchase_hist.query.with_entities(
                    Purchase_hist.purchase_date, Purchase_hist.start_date, Purchase_hist.end_date
                ).filter(
                    Purchase_hist.tbl_customer_id == list_user[i]
                ).all()
            if bool(purchase_history):
                limit_email = []
                limit_block = []
                for j in range(0, len(purchase_history)):
                    purchase_date = today - purchase_history[j][0]
                    start_date = today - purchase_history[j][1]
                    end_date = today - purchase_history[j][2]

                    if (int(purchase_date.days) > 25 and int(purchase_date.days) < 30) or (
                            int(start_date.days) > 25 and int(start_date.days) < 30) or (
                            int(end_date.days) > 25 and int(end_date.days) < 30):
                        limit_email.append(1)
                    if (int(purchase_date.days) >= 30 or int(start_date.days) >= 30 or int(end_date.days) >= 30):
                        limit_block.append(1)

                if(len(limit_email)>0):
                    is_mail_sent = BlockUserlog.query.filter(
                            and_(
                                BlockUserlog.tbl_customer_id == list_user[i], 
                                BlockUserlog.mail_sent_date == today
                            )
                        ).first()
                    
                    if not(is_mail_sent):
                        block_user_log = BlockUserlog(
                            tbl_customer_id = list_user[i],
                            mail_sent_date = today,
                            mail_block_user = 1
                        )
                        db.session.add(block_user_log)
                        db.session.commit()

                        print('Compose Mail for Plan will Expire.')
                if(len(limit_block)>0):
                    block = Customer.query.filter(Customer.customer_id == list_user[i]).first()
                    block.block_user = 1
                    db.session.commit()
                    print('Compose Mail for Plan Expired.')     
            else:
                customer_registered_date = Customer.query.with_entities(Customer.registration_date).filter(
                    Customer.tbl_customer_id == list_user[i]).all()
                if bool(customer_registered_date):
                    limit_email = []
                    limit_block = []
                    for j in range(0, len(customer_registered_date)):
                        registered_date = today - customer_registered_date[j][0]

                        if(int(registered_date.days)>25 and int(registered_date.days)<30):
                            limit_email.append(1)
                        if(int(registered_date)>=30):
                            limit_block.append(1)
                    
                    if(len(limit_email)>0):
                        is_mail_sent = BlockUserlog.query.filter(
                            and_(
                                BlockUserlog.tbl_customer_id == list_user[i], 
                                BlockUserlog.mail_sent_date == today
                            )
                        ).first()
                    
                    if not(is_mail_sent):
                        block_user_log = BlockUserlog(
                            tbl_customer_id = list_user[i],
                            mail_sent_date = today,
                            mail_block_user = 1
                        )
                        db.session.add(block_user_log)
                        db.session.commit()

                        print('Compose Mail for Plan will Expire.')
                if(len(limit_block)>0):
                    block = Customer.query.filter(Customer.customer_id == list_user[i]).first()
                    block.block_user = 1
                    db.session.commit()
                    print('Compose Mail for Plan Expired.')

@admin.route('/admin/plan_details', methods=["GET"])
@admin_auth
def admin_plan_details():
    admin_location = Admin.query.with_entities(Admin.tbl_location_id).filter(Admin.admin_email == g.token).first()
    print(admin_location[0])
    if bool(admin_location):
        plans = Subscription_plan.query.join(
                Plan_price, Subscription_plan.plan_id == Plan_price.tbl_plan_id
            ).with_entities(Subscription_plan.plan_id, Subscription_plan.capacity, Subscription_plan.duration, Plan_price.price, Subscription_plan.discount).filter(
                Plan_price.tbl_location_id == admin_location[0]
            ).all()
        
        if bool(plans):
            json_list=[]
            for i in range(0, len(plans)):
                if plans[i][1] == 1:
                    plan_type = "Solo"
                elif plans[i][1] == 2:
                    plan_type = "Dual"
                elif plans[i][1] == 4:
                    plan_type = "Quad"
    
                value = {
                    "plan_id": plans[i][0],
                    "plan_type": plan_type,
                    "validity": plans[i][2],
                    "plan_price": plans[i][3],
                    "discount": plans[i][4]
                }

                json_list.append(value)
            resp = make_response({
                "status_code": 200,
                "location_plans": json_list
            })
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
            return resp
        else:
            resp = make_response({
                "status_code": 404,
                "message": "No Plans at current location."
            })
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
            return resp
    else:
        resp = make_response({
            "status_code": 404,
            "message": "Admin doesn't exist."
        })
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

@admin.route('/admin/desk_details',methods = ["GET"])
@admin_auth
def admin_desk_details():
                # Admin.tbl_location_id,Plan_price.plan_price_id
    search_date = request.args.get("date")
    if search_date == '':
        search_date = date.today()
    location = db.session.query(Admin,Location).with_entities(
            Location.capacity,Location.location_id
                ).filter(
                    Admin.admin_email == g.token , Admin.tbl_location_id == Location.location_id
                ).first()

    desk_details = db.session.query(Customer,Plan_price,Purchase_hist).with_entities(
        Purchase_hist.desk_no,Purchase_hist.end_date,Customer.name
                ).filter(
                    Plan_price.tbl_location_id == location["location_id"],Purchase_hist.tbl_plan_price_id == Plan_price.plan_price_id,Purchase_hist.start_date<=search_date,Purchase_hist.end_date>=search_date,Purchase_hist.tbl_customer_id == Customer.customer_id
                ).all()
    # print(location)

    desk_detail_list = [ {"desk_no":i+1,"booked":0} for i in range(location['capacity']) ]

    for i in desk_details:
        for j in i['desk_no'].split(","):
            # print(j)
            desk_detail_list[int(j)-1]["booked"]=1
            desk_detail_list[int(j)-1]["expiry_date"]=i['end_date'].strftime("%Y-%m-%d")
            desk_detail_list[int(j)-1]["customer_name"]=i['name']



    resp = make_response(
            {
                "status_code": 200,
                "desks":desk_detail_list,
                # "date":date,
                "message": "Desk details fetched Successfully"
            }
        )
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp



@admin.route('/admin/desks',methods = ["GET"])
@admin_auth
def admin_desk_status():

    number_of_desks = db.session.query(Admin,Location).with_entities(
        Location.capacity
    ).filter(
        Admin.tbl_location_id == Location.location_id , Admin.admin_email == g.token
    ).first()
    resp = make_response(
        {
            "status_code": 200,
            "desks": number_of_desks["capacity"],
            # "date":date,
            "message": "No one have purchase any plan"
        }
    )
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


@admin.route('/admin/desk_statistics',methods = ["GET"])
@admin_auth
def admin_desk_statistics():

    desk_no = request.args.get("desk_no")
    search_date = date.today()
    location = db.session.query(Admin,Location).with_entities(
            Location.location_id
                ).filter(
                    Admin.admin_email == g.token , Admin.tbl_location_id == Location.location_id
                ).first()

    desk_details = db.session.query(Plan_price,Purchase_hist).with_entities(
        Purchase_hist.desk_no,Purchase_hist.end_date,Purchase_hist.start_date
                ).filter(
                    Plan_price.tbl_location_id == location["location_id"],Purchase_hist.tbl_plan_price_id == Plan_price.plan_price_id,Purchase_hist.end_date>=search_date#Purchase_hist.start_date<=search_date,Purchase_hist.end_date>=search_date,Purchase_hist.tbl_customer_id == Customer.customer_id
                ).all()

    booked_dates =[]

    for i in desk_details:
        if str(desk_no) in i['desk_no'].split(","):
            booked_dates.append([i['start_date'].strftime("%Y-%m-%d"),i['end_date'].strftime("%Y-%m-%d")])
            

    resp = make_response(
        {
            "status_code": 200,
            "booking_dates": booked_dates,
            # "date":date,
            "message": "No one have purchase any plan"
        }
    )
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp
