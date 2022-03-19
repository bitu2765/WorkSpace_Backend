from flask import Blueprint,make_response,render_template,request
import uuid
import hashlib
from app import db,mail
from models import Customer

from flask_mail import Mail, Message
# from flaskr import var
from models import Customer
user = Blueprint('user',__name__)


@user.route('/send_mail', methods=['GET'])
def send_mail():
    msg = Message(
        'Hello, From Motorola',
        sender='veetmoradiya7823@gmail.com',
        recipients=['bhautiksudani2765@gmail.com']
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return "Send Successfully"


@user.route('/user/register', methods=['POST'])
def temp_user_registration():
    # print(1)
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            data = request.json
            sender_uuid = uuid.uuid4()
            customer_id = data['customer_id']
            name = data['name']
            email = data['email']
            mobile_no = data['mobile_no']
            password = data['password']
            # print(name, email, mobile_no, password, sender_uuid)
            exist = bool(db.session.query(Customer).filter_by(email=email,
                                                              mobile_no=mobile_no,
                                                              customer_id=customer_id).first())
            if exist:
                return {"message": "Email already exists or mobile no "
                                   "is already exist or username already taken", "status_code": 404}
            else:
                user_data = Customer(sender_uuid=sender_uuid,
                                     customer_id=customer_id,
                                     name=name,
                                     email=email,
                                     mobile_no=mobile_no,
                                     password=password)
                db.session.add(user_data)
                db.session.commit()
                # mail code
                msg = Message(
                    'Hello, From ',
                    sender='veetmoradiya7823@gmail.com',
                    recipients=[email]
                )
                # obj = urlparse(request.base_url)
                verify_url = str('http://' + request.host + '/verify_user?token=' + str(sender_uuid))
                print(verify_url)
                msg.body = 'Hello User, please verify your self by clicking on this link \nLink : '+verify_url
                mail.send(msg)

                return {"message": "User Successfully registered. "
                                   "please verify your self link is send to your registered mail id.", "status_code": 200}
        else:
            return {"message": "Content-Type not supported!"}


@user.route('/verify_user', methods=['GET'])
def verify_user():
    tkn = str(request.args.get('token'))
    exist = bool(db.session.query(Customer).filter_by(token=tkn).first())
    print(exist)
    if exist:
        user_detail = Customer.query.filter_by(token=tkn).first()
        if user_detail.email_verify:
            return {"message":"User email already verified, please login now."}
        else:
            user_detail.email_verify = True
            db.session.commit()
            return {"message": "User with this token exists and verified", "status_code": 200}
    else:
        return {"message": "User with this token not exists. please register your self priorly", "status_code": 403}

@user.route("/user/<id>", methods=['GET'])
def user_profile(id):
    info = Customer.query.with_entities(Customer.name, Customer.email, Customer.mobile_no).filter_by(customer_id=id).first()
    if bool(info):
        return {
            "customer": {
                id: {
                    "name": info[0],
                    "email": info[1],
                    "mobile_no": info[2]
                }
            }
        }
    else:
        return{
            "message": "User: "+id+" doesn't exist."
        }

# app.register_blueprint(test)