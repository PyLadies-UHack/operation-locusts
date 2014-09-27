from flask import request, render_template
from app.users import users
from app.users.models import User

@users.route("", methods=["GET"])
@users.route("/<int:page>", methods=["GET"])
def index(page=1):
    """
    Returns a list of users
    """
    
    users = User.query.limit(10).all()    

    print(len(users))

    return render_template("users/index.html", users=users)
