from flask import Flask, render_template
from pymongo import MongoClient


app = Flask(__name__)

app.config.from_object('settings')

db = MongoClient()['locust']

#from app.users import users

#app.register_blueprint(users, url_prefix="/users")


from app.views import *

def init():
    
    
    db.drop_collection('users')
    db.drop_collection('organizations')
    
    users = db['users']
    orgs = db['organizations']

    import json
    
    obj = json.loads(open('app/init.json').read())
    
    new_users = obj['users']
    new_orgs = obj['organizations']

    users.insert(new_users)
    orgs.insert(new_orgs)



app.before_first_request(init)
