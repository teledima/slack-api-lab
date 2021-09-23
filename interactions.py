import json
from flask import Blueprint, request, make_response, jsonify
from slack_sdk import WebClient
from slack_sdk.models.blocks import PlainTextObject, SectionBlock, ActionsBlock, ButtonElement
from slack_sdk.errors import SlackApiError
import config
import datetime as dt
from utils import get_view, get_document
from email_validator import validate_email, EmailNotValidError

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_endpoint():
    payload = json.loads(request.form['payload'])
    if payload['type'] == 'block_actions':
        pass
    elif payload['type'] == 'view_submission':
        callback_id = payload['view']['callback_id']
        pass
    return make_response('', 200)

