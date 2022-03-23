from flask import Blueprint,make_response,render_template,request

from app import db,mail
from models import Subscription_plan,Plan_price,Location

site = Blueprint('site',__name__)

# sub = Blueprint('subscription',__name__)

# api to get all plans details

@site.route('/plans',methods = ['GET'])
def plans():

    plansInfo = db.session.query(Plan_price, Subscription_plan).filter(Plan_price.tbl_plan_id == Subscription_plan.plan_id).all()
    if bool(plansInfo):
        
        discount = planPrice = validity = planType = None
        # print ("plan price Id: {} location Id: {} plan Id No: {} price: {}".format(p.plan_price_id,p.tbl_location_id, p.tbl_plan_id, p.price))            
            
        records = []    
            
        for p,s in db.session.query(Plan_price, Subscription_plan).filter(Plan_price.tbl_plan_id == Subscription_plan.plan_id).all():
            # print ("plan price Id: {} location Id: {} plan Id No: {} price: {}".format(p.plan_price_id,p.tbl_location_id, p.tbl_plan_id, p.price))               
            discount = str(s.discount)
            planPrice = str(p.price)
            validity = str(s.duration)
            planType = "Solo" if (s.capacity == 1) else "Duo" if (s.capacity == 2)  else "Squade"
        
            obj = {
                'plan_type' : planType,
                'validity' : validity,
                'plan_price' : planPrice,
                'discount' : discount
            }
        
            records.append(obj)
            # print(planType," ",planPrice," ",validity," ",dis," ",location,"\n")

        # records = json.dumps(records)
        # return (records)
        resp = make_response(
            {
                "status_code":200,
                "plans": records
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
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


# api to get plans for specific location with location_id

@site.route("/plans/<location_id>", methods= ['GET'])
def plans_for_location(location_id):
    # location_plans = db.session.query(Plan_price).filter(Plan_price.tbl_location_id == location_id).all()
    
    plansInfo = db.session.query(Plan_price, Subscription_plan).filter(Plan_price.tbl_location_id == location_id, Plan_price.tbl_plan_id == Subscription_plan.plan_id).all()
    if bool(plansInfo):
        
        discount = planPrice = validity = planType = None
        # print ("plan price Id: {} location Id: {} plan Id No: {} price: {}".format(p.plan_price_id,p.tbl_location_id, p.tbl_plan_id, p.price))            
            
        records = []    
            
        for p,s in db.session.query(Plan_price, Subscription_plan).filter(Plan_price.tbl_location_id == location_id, Plan_price.tbl_plan_id == Subscription_plan.plan_id).all():
            # print ("plan price Id: {} location Id: {} plan Id No: {} price: {}".format(p.plan_price_id,p.tbl_location_id, p.tbl_plan_id, p.price))               
            discount = str(s.discount)
            planPrice = str(p.price)
            validity = str(s.duration)
            planType = "Solo" if (s.capacity == 1) else "Duo" if (s.capacity == 2)  else "Squade"
        
            obj = {
                'plan_type' : planType,
                'validity' : validity,
                'plan_price' : planPrice,
                'discount' : discount
            }
        
            records.append(obj)
            
        # records = json.dumps(records)
        # return (records)
        resp = make_response(
            {
                "status_code":200,
                "Location_plans": records
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code":404,
                "message": "Their is No any Plans exist Currently."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

        