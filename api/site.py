from flask import Blueprint, make_response, render_template, request
import routes
import logging
from app import db, mail
from models import Subscription_plan, Plan_price, Location

site = Blueprint('site', __name__)

# logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler = logging.FileHandler('logs/plan_details.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# sub = Blueprint('subscription',__name__)

# api to get all plans details
@site.route('/plans', methods=['GET'])
def plans():
    subscription_plans = Subscription_plan.query.all()
    subscription_plan_list = []

    for plan in subscription_plans:
        plan_name = ""
        if plan.capacity == 1:
            plan_name = "Single"
        elif plan.capacity == 2:
            plan_name = "Double"
        elif plan.capacity == 4:
            plan_name = "Quad"
        _plan = {
            "plan_name": plan_name,
            "capacity": plan.capacity,
            "duration": plan.duration,
            "discount": plan.discount
        }
        subscription_plan_list.append(_plan)

    resp = make_response({
        "status_code": 200,
        "plans": subscription_plan_list
    })
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    # log
    logger.info('Api called to get all plans details')
    return resp


# api to get plans for specific location with location_id
@site.route("/plans/<location_id>", methods=['GET'])
def plans_for_location(location_id):
    # location_plans = db.session.query(Plan_price).filter(Plan_price.tbl_location_id == location_id).all()

    plansInfo = db.session.query(Plan_price, Subscription_plan).filter(Plan_price.tbl_location_id == location_id,
                                                                       Plan_price.tbl_plan_id == Subscription_plan.plan_id).all()
    if bool(plansInfo):

        discount = planPrice = validity = planType = None
        records = []

        for p, s in plansInfo:
            discount = str(s.discount)
            planPrice = str(p.price)
            validity = str(s.duration)
            planType = "Solo" if (s.capacity == 1) else "Duo" if (s.capacity == 2) else "Squade"

            obj = {
                'plan_type': planType,
                'validity': validity,
                'plan_price': planPrice,
                'discount': discount
            }

            records.append(obj)

        # records = json.dumps(records)
        # return (records)
        resp = make_response(
            {
                "status_code": 200,
                "Location_plans": records
            }
        )
        # log
        logger.info('Api called to get plan for location - {0}'.format(location_id))
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    else:
        resp = make_response(
            {
                "status_code": 404,
                "message": "Their is No any Plans exist Currently."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp


# retrieve all locations
@site.route('/locations', methods=['GET'])
def locations():
    query = db.session.query(Location).all()
    record = []
    if bool(query):
        for l in query:
            city = l.city
            state = l.state
            id = l.location_id
            add =l.address
            
            obj = {
                'id' : id,
                'add' : add,
                'city' : city,
                'state' : state
            }

            record.append(obj)

        resp = make_response(
            {
                "status_code": 200,
                "Locations": record
            }
        )
        # log
        logger.info('Api called to get all available locations')
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    else:
        resp = make_response(
            {
                "status_code": 404,
                "message": "Their is No location available currently."
            }
        )
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
