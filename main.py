import os
import json

with open('api-slack-lab-53bc9f64d71c.json', 'r') as service_account_file, \
     open('api-slack-lab-firebase-adminsdk-i0a4u-763d93416c.json') as firebase_account_file:
    service_account_key = json.load(service_account_file)
    firebase_account_key = json.load(firebase_account_file)

os.environ['SERVICE_ACCOUNT_KEY'] = str(service_account_key).replace('\'', '"')
os.environ['FIREBASE_ACCOUNT_KEY'] = str(firebase_account_key).replace('\'', '"')

import config
import firebase_admin
from firebase_admin import credentials

from flask import Flask
from auth import auth_blueprint
from events import event_blueprint
from interactions import interaction_blueprint

cred = credentials.Certificate(config.firebase_account_key)
firebase_admin.initialize_app(cred)

app = Flask(__name__)
app.register_blueprint(auth_blueprint)
app.register_blueprint(event_blueprint)
app.register_blueprint(interaction_blueprint)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'
