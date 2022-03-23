import json
from flask import Blueprint,make_response,render_template,request, g
from app import db
from models import Admin, Customer, Location, Subscription_plan, Plan_price, Purchase_hist
from userauth import admin_auth
from datetime import date

admin = Blueprint('admin',__name__)

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
    users = Customer.query.all()
    user_list = []
    for user in users:
        _user = {
            "name": user.name,
            "email": user.email,
            "email_verified": user.email_verify,
            "is_block": user.block_user
        }
        user_list.append(_user)
    resp = make_response({
        "status_code": 200,
        "customers": user_list
    })
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp