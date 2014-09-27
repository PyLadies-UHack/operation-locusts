from flask import render_template
from flask.ext.user import login_required

from app import app

@login_required
@app.route("/")
def index():
    return render_template('index.html')
