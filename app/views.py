from flask import render_template
from flask.ext.user import current_user, login_required
from app import app

@app.route("/")
def index():
    """
    Renders the home page
    """

    print(dir(current_user))

    if current_user.is_authenticated():
        if "user" in current_user.roles:
            return render_template('user_index.html')
        elif "locust" in current_user.roles:
            return render_template('locust_index.html')
        else:
            return render_template('locust_index.html')


    return render_template('index.html')
    


