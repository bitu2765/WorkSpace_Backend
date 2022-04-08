from app import app

from api.test import test
from api.login import log
from api.admin import admin
from api.site import site
from api.user import user


app.register_blueprint(test)
app.register_blueprint(log)
app.register_blueprint(admin)
app.register_blueprint(site)
app.register_blueprint(user)
