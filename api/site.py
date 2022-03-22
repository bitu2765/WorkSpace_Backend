from flask import Blueprint,make_response,render_template,request

from app import db,mail
from models import Subscription_plan

site = Blueprint('site',__name__)

    
