import json
from flask import Blueprint
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient

import config


event_blueprint = Blueprint('event_blueprint', import_name=__name__)
event_adapter = SlackEventAdapter(config.signing_secret, endpoint='/event-endpoint', server=event_blueprint)


@event_adapter.on('app_home_opened')
def event_endpoint(event_data):
    with open('views/home.json', 'r', encoding='utf-8') as view_file:
        home_view = json.load(view_file)
    WebClient(token=config.bot_token).views_publish(view=home_view, user_id=event_data['event']['user'])
