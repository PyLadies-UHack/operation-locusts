from flask import render_template
from flask.ext.user import current_user, login_required
from app import app

@app.route("/")
def index():
    """
    Renders the home page
    """

    if current_user.is_authenticated():
        if current_user.has_roles(['user']):
            return render_template('user_index.html')
        elif current_user.has_roles(['locust']):
            return render_template('locust_index.html')
        else:
            return render_template('locust_index.html')


    return render_template('index.html')
    


