from flask import g, render_template, redirect, url_for, session, request
from passlib.hash import bcrypt
from app import app, db
from app.forms import LoginForm, LogoutForm, RevokeForm
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from functools import wraps
import json

@app.before_request
def user():
    if 'email' in session:
        user = db.users.find_one({'email': session['email']})
        if user:
            g.user = user
            g.logout = LogoutForm(meta={'csrf_context': session})

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=['GET'])
def index():
    """
    Renders the home page
    """

    return render_template('index.html')


@login_required
@app.route("/badges/<slug>", methods=['GET'])
def badges(slug):
        
    badge = db.badges.find_one({
        'organization': g.user['organization'],
        'slug': slug
    })

    if not badge:
        return "Badge not found", 404
      
    b = None

    for ub in g.user['badges']:
        if badge['id'] == ub['id']:
            b = badge
            b['completeness'] = int((ub['value'] / ub['goal']) * 100)
            b['complete'] = ub['status'] == 'complete'
            break
     
    if not b:
        return "You are not participating in this badge", 304

    context = {
        "badge": b,
    }

    
    return render_template('badge.html', **context)
        


def grant_badge(id, email):

    api_key = 'gZZDY3UwGe9oojWX19qx'
    base = 'https://sandbox.youracclaim.com/api/v1'
    org = 'ac7e8f74-5e79-411a-b5b9-d0ee0384f42c'

    url = "{base}/organizations/{org}/badges".format(base=base, org=org)

    data = {
        "recipient_email": "andrew@clarkson.mn",
        "badge_template_id": id,
        "issued_at": str(datetime.now()) 
    }

    requests.post(url, data=data, auth=HTTPBasicAuth(api_key, ''))

@login_required    
@app.route("/badges/<slug>/checkin", methods=["POST"])
def checkin(slug):
            
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])


    badge = db.badges.find_one({'slug': slug, 'locations': 
        {"$geoWithin": {"$center": [[lat, lng], 0.02]}}})

            
    if not badge:
        return "", 500

    for b in g.user['badges']:
        if b['id'] == badge['id']:
            if b['status'] == "in-progress":
                b['value'] += 1
                if b['value'] == b['goal']:
                    b['status'] = "completed"

                    grant_badge(b['id'], g.user['email'])

                db.users.save(g.user)

    return "", 201
    
@login_required
@app.route("/profile", methods=["GET"])
def profile():

    badges = g.user['badges']

    for badge in badges:
        b = db.badges.find_one({"id": badge['id']})    
        badge['name'] = b['name']
        badge['image'] = b['image_url']
        badge['slug'] = b['slug']
        badge['completeness'] = int((badge['value'] / badge['goal']) * 100)

    return render_template('profile.html')

@login_required
@app.route("/manage", methods=['GET'])
def manage():
   
    sort = request.args.get('sort', 'date')
    
    api_key = 'gZZDY3UwGe9oojWX19qx'
    base = 'https://sandbox.youracclaim.com/api/v1'
    org = 'ac7e8f74-5e79-411a-b5b9-d0ee0384f42c'

    url = "{base}/organizations/{org}/badges".format(base=base, org=org)

    order = "issued_at"

    if sort == "badge": 
        order = "badge_templates[name]"
    elif sort == "user":
        order = "user[last_name]" 
        
    params = {
        "sort": order         
    }

    r = requests.get(url, data=params, auth=HTTPBasicAuth(api_key, ''))

    form = RevokeForm(meta={'csrf_context': session})

    data = []
    for entry in r.json()['data']:
        entry['time'] = datetime.strptime(entry['issued_at'][:10], "%Y-%M-%d")
        data.append(entry)

    return render_template('manage.html', form=form, sort=sort, data=data)


@login_required
@app.route("/manage/revoke", methods=['POST'])
def revoke():
    
    api_key = 'gZZDY3UwGe9oojWX19qx'
    base = 'https://sandbox.youracclaim.com/api/v1'
    org = 'ac7e8f74-5e79-411a-b5b9-d0ee0384f42c'
    

    form = RevokeForm(request.form, meta={'csrf_context': session})

    if form.validate():

        url = "{base}/organizations/{org}/badges/{id}/revoke".format(base=base, org=org, id=form.id.data)
        
        r = requests.put(url, data={'reason': 'failure'}, auth=HTTPBasicAuth(api_key, ''))

        if r.status_code == 200: 
            return redirect(url_for('manage'))
    
    return "", 500


@login_required
@app.route("/manage/users", methods=['GET'])
def manage_users():
    org = g.user['organization']
    users = db.users.find({'organization': org, 'role': 'user'})

    return render_template('users.html', users=users)

@login_required
@app.route("/manage/users/<id>", methods=['GET'])
def manage_user(id):   
    org = g.user['organization']

    user = db.users.find_one({'id': id, 'organization': org, 'role': 'user'})


    b = []
    for badge in user['badges']:
        b.append(db.badges.find_one({'id': badge['id']}))

    return render_template('user.html', badges=b, user=user)
    

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

            if user['role'] == 'manager':
                return redirect(url_for('manage'))
            else:
                return redirect(url_for('profile'))
        
        else:
            error = "Wrong email password combination"
    

    return render_template("login.html", error=error, form=form)


@app.route("/logout", methods=["POST"])
def logout():
    form = LogoutForm(request.form, meta={'csrf_context': session})
    if form.validate:
        session.pop('email', None)

    return redirect(url_for('index'))
