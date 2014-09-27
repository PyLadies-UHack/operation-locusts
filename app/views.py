from flask import render_template, redirect, url_for, session, request
from passlib.hash import bcrypt
from app import app, db
from app.forms import LoginForm, LogoutForm


@app.route("/", methods=['GET'])
def index():
    """
    Renders the home page
    """

    if 'email' in session:

        user = db.users.find_one({'email': session['email']})

        if not user:
            return "Bad Session"

        if user['role'] == 'user':
            return render_template('user.html')
        elif user['role'] == 'manager':
            return render_template('manager.html')
    else:
        return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm(request.form, meta={'csrf_context': session})

    error = None

    if request.method == 'POST' and form.validate():

        email = form.email.data
        password = form.password.data
        
        user = db.users.find_one({'email': email})

    

        if user and bcrypt.verify(password, user['password'],):
            
            session['email'] = email
            
            return redirect(url_for('index'))
        
        else:
            error = "Wrong email password combination"
    

    return render_template("login.html", error=error, form=form)


@app.route("/logout", methods=["POST"])
def logout():
    form = LogoutForm(request.form, meta={'csrf_context': session})
    if form.validate:
        session.pop('email', None)

    redirect(url_for('index'))
