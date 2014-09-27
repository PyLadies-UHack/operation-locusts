from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('settings')

db = SQLAlchemy(app)

from app.users import users

app.register_blueprint(users, url_prefix="/users")

db.create_all()


@app.route("/")
def index():
    return "Hello World"
