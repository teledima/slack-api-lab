from flask import Blueprint

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_blueprint():
    pass
