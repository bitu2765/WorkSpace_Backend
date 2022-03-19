from flask import Blueprint,make_response,render_template,request

from app import db,mail
from models import Subscription_plan

site = Blueprint('site',__name__)

@site.route('/plans')
def site_plans():

    plans = Subscription_plan.query.all()
    print(plans)
    return make_response({'Msg':"plans are here!"})
    
