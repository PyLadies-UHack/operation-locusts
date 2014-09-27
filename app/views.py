from flask import render_template, redirect, url_for, session, request
from passlib.hash import bcrypt
from app import app, db
from app.forms import LoginForm, LogoutForm
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

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
                "ubadge": ubadge,
                "badge": badge,
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


def grant_badge(slug, email):

    api_key = 'gZZDY3UwGe9oojWX19qx'
    base = 'https://sandbox.youracclaim.com/api/v1'
    org = 'ac7e8f74-5e79-411a-b5b9-d0ee0384f42c'

    url = "{base}/organizations/{org}/badges".format(base=base, org=org)

    data = {
        "recipient_email": "andrew@clarkson.mn",
        "badge_template_id": slug,
        "issued_at": str(datetime.now()) 
    }

    request.post(url, data=data, auth=HTTPBasicAuth(self.api_key, ''))

    
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
    

            location = db.badges.find_one({'locations': 
                {"$geoWithin": {"$center": [[lat, lng], 0.02]}}})

            
            if not location:
                return "", 500

            for badge in user['badges']:
                if badge['slug'] == slug:
                    if badge['status'] == "in-progress":
                        badge['value'] += 1
                        if badge['value'] == badge['goal']:
                            badge['status'] = "completed"

                            grant_badge(badge['slug'], user['email'])

                        db.users.save(user)




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
