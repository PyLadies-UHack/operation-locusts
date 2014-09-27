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
    db.drop_collection('badges')
    
    users = db['users']
    orgs = db['organizations']
    badges = db['badges']

    import json
    
    obj = json.loads(open('app/init.json').read())
    
    new_users = obj['users']
    new_orgs = obj['organizations']
    new_badges = obj['badges']

    users.insert(new_users)
    badges.insert(new_badges)
    orgs.insert(new_orgs)



app.before_first_request(init)
