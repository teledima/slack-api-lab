from flask import Blueprint, request
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock, UserSelectElement, ActionsBlock, ButtonElement
from firebase_admin import firestore
from utils import get_view, get_document

import config


event_blueprint = Blueprint('event_blueprint', import_name=__name__)
event_adapter = SlackEventAdapter(config.signing_secret, endpoint='/event-endpoint', server=event_blueprint)


@event_adapter.on('app_home_opened')
def event_endpoint(event_data):
    home_view_init = get_view('views/home_init.json')
