import json
from flask import Blueprint,make_response,render_template,request

from app import db,mail
from models import Subscription_plan,Plan_price,Location

site = Blueprint('site',__name__)

# sub = Blueprint('subscription',__name__)

@site.route('/plans',methods = ['GET'])
def plans():

    plansInfo = db.session.query(Plan_price, Subscription_plan,Location).filter(Plan_price.tbl_plan_id == Subscription_plan.plan_id,Plan_price.tbl_location_id == Location.location_id).all()
    if bool(plansInfo):
        
        dis = planPrice = validity = location = planType = None
        # print ("plan price Id: {} location Id: {} plan Id No: {} price: {}".format(p.plan_price_id,p.tbl_location_id, p.tbl_plan_id, p.price))            
            
        records = []    
            
        for p,s,l in db.session.query(Plan_price, Subscription_plan,Location).filter(Plan_price.tbl_plan_id == Subscription_plan.plan_id,Plan_price.tbl_location_id == Location.location_id).all():
            # print ("plan price Id: {} location Id: {} plan Id No: {} price: {}".format(p.plan_price_id,p.tbl_location_id, p.tbl_plan_id, p.price))               
            dis = str(s.discount)
            planPrice = str(p.price)
            location = l.city
            validity = str(s.duration)
            planType = "Solo" if (s.capacity == 1) else "Duo" if (s.capacity == 2)  else "Squade"
        
            obj = {
                'plan_type' : planType,
                'location' : location,
                'validity' : validity,
                'plan_price' : planPrice,
                'discount' : dis
            }
        
            records.append(obj)
            # print(planType," ",planPrice," ",validity," ",dis," ",location,"\n")

        records = json.dumps(records)
        return (records)
    else:
        resp = make_response(
            {
                "status_code":404,
                "message": "Their is No any Plans exist Currently."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

# return "Subscription Api"    
