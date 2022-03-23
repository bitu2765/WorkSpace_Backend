from flask import Blueprint, make_response, render_template, request
from app import db
from models import Admin, Location, Purchase_hist, Customer

admin = Blueprint('admin', __name__)


@admin.route('/admin/profile', methods=['GET'])
def admin_profile():
    info = Admin.query.join(Location, Admin.tbl_location_id == Location.location_id).with_entities(Admin.admin_email,
                                                                                                   Admin.admin_name,
                                                                                                   Location.address,
                                                                                                   Location.city,
                                                                                                   Location.state).first()
    return {
        "admin": {
            "email": info[0],
            "name": info[1],
            "address": info[2],
            "city": info[3],
            "state": info[4]
        }
    }


# all users details for admin side to show list of users
@admin.route('/admin/user_details', methods=['GET'])
def users_details():
    users = Customer.query.all()
    user_list = []
    for user in users:
        user = {
            "name": user.name,
            "email": user.email,
            "email_verified": user.email_verify,
            "is_block": user.block_user
        }
        user_list.append(user)
    resp = make_response({
        "status_code": "200",
        "customers": user_list
    })
    return resp
