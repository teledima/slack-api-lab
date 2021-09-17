from flask import Blueprint

auth_blueprint = Blueprint(name='auth_blueprint', import_name=__name__)


@auth_blueprint.route('/auth')
def auth():
    pass
