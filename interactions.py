from flask import Blueprint, request, make_response

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_endpoint():
    return make_response('', 501)
