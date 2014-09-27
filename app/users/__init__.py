from flask import Blueprint
from app.users.models import User

users = Blueprint("users", __name__)

@users.route("")
def index():
    """
    Return a page of users
    """
    return "TODO"
