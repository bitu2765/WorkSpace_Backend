from flask import Blueprint,make_response,render_template,request
from app import db
from models import Admin, Location
admin = Blueprint('admin',__name__)

@admin.route('/admin/profile', methods=['GET'])
def admin_profile():
    info = Admin.query.join(Location, Admin.tbl_location_id == Location.location_id).with_entities(Admin.admin_email, Admin.admin_name, Location.address, Location.city, Location.state).first()
    return {
        "admin": {
            "email": info[0],
            "name": info[1],
            "address": info[2],
            "city": info[3],
            "state": info[4]
        }
    }
