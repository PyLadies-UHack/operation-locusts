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

        logout = LogoutForm(meta={'csrf_context': session})

        if user['role'] == 'user':


            context = {
                "name": user['name'],
                "organization": user['organization'],
                "badges": user['badges'],
                "logout": logout
            }

            return render_template('user.html', **context)
        
        elif user['role'] == 'manager':
            
            context = {
                "name": user['name'],
                "organization": user['organization'],
                "logout": logout
            }
            
            return render_template('manager.html', **context)
    else:

        return render_template('index.html')

@app.route("/badges/<slug>", methods=['GET'])
def badges(slug):
    
    if 'email' in session:

        user = db.users.find_one({'email': session['email']})
        
        if not user:
            return "Bad Session"

        logout = LogoutForm(meta={'csrf_context': session})
        
        if user['role'] == 'user':


            badge = db.badges.find_one({
                'organization': user['organization'],
                'slug': slug
            })

            if not badge:
                return "Badge not found", 404

            
            ubadges = user['badges']

            ubadge = None
            for b in ubadges:
                if b['slug'] == slug:
                    ubadge = b
                    break
            
            if not ubadge:
                return "You are not working on this badge", 404

            context = {
                "name": user['name'],
                "organization": user['organization'],
                "user_steps": ubadge['steps'],
                "badge_steps": badge['steps'],
                "logout": logout
            }

            return render_template('user_badge.html', **context)
        
        elif user['role'] == 'manager':
            
            context = {
                "name": user['name'],
                "organization": user['organization'],
                "logout": logout
            }
            
            return render_template('manager_badge.html', **context)
    
    else:

        return redirect(url_for('login'))

    
@app.route("/badges/<slug>/checkin", methods=["POST"])
def checkin(slug):
    if 'email' in session:

        user = db.users.find_one({'email': session['email']})
        
        if not user:
            return "Bad Session"

        logout = LogoutForm(meta={'csrf_context': session})
        
        if user['role'] == 'user':
            
            lat = float(request.form['lat'])
            lng = float(request.form['lng'])

            

            location = db.badges.find_one({'location': 
                {"$within": {"$center": [[lat, lng], 1]}}})
            
            print(location)

            return "", 200



        else:

            return "You are not working on this badge", 404
    
    else:

        return redirect(url_for('login'))
    



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
