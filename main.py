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
