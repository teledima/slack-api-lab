from flask import Flask
from auth import auth_blueprint

app = Flask(__name__)
app.register_blueprint(auth_blueprint)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'
