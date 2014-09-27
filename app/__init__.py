from flask import Flask, render_template
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('settings')

babel = Babel(app)
db = SQLAlchemy(app)

from app.users import users

app.register_blueprint(users, url_prefix="/users")

db.create_all()

from app.views import *

