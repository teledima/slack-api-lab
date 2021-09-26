from flask import Flask
from auth import auth_blueprint
from events import event_blueprint
from interactions import interaction_blueprint

app = Flask(__name__)
app.register_blueprint(auth_blueprint)
app.register_blueprint(event_blueprint)
app.register_blueprint(interaction_blueprint)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'
