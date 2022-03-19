from flask import Blueprint,make_response,render_template,request,g
from userauth import user_auth
import uuid
import hashlib
from app import db,mail

from flask_mail import Mail, Message
# from flaskr import var
from models import Customer
test = Blueprint('test',__name__)

@test.route('/test')
def testing():
    return "Testing Page!!"


@test.route('/auth')
@user_auth
def testing2():
    return f'Authenticated user is {g.token} . '

