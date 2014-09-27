from flask.ext.user import UserManager, UserMixin, SQLAlchemyAdapter
from app import app, db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)
