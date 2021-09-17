from flask import Blueprint

event_blueprint = Blueprint('event_blueprint', import_name=__name__)


@event_blueprint.route('/event-endpoint', methods=['POST'])
def event_endpoint():
    pass
