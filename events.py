import json

from flask import Blueprint, request
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock, ChannelSelectElement, ActionsBlock, ButtonElement, ConfirmObject
from firebase_admin import firestore
from utils import get_view, get_document

import config


event_blueprint = Blueprint('event_blueprint', import_name=__name__)
event_adapter = SlackEventAdapter(config.signing_secret, endpoint='/event-endpoint', server=event_blueprint)


@event_adapter.on('app_home_opened')
def event_endpoint(event_data):
    home_view_init = get_view('views/home_init.json')
    user_id_opened = event_data['event']['user']
    user_doc = get_document(config.db, collection_id='authed_users', document_id=user_id_opened)

    text = 'Добро пожаловать в панель управления каналами!\n'
    # if user_doc exist then user is authenticated
    if user_doc:
        home_view_init['blocks'] += [
            SectionBlock(text=text +
                              'Здесь вы можете просмотреть информацию о выбранном канале, создавать или удалять каналы, '
                              'а также изменять названия каналов.', block_id='welcome_block').to_dict(),
            SectionBlock(text='Выберите канал из списка',
                         accessory=ChannelSelectElement(placeholder='Название канала', action_id='channel_select_action'),
                         block_id='channel_select_block').to_dict(),
            ActionsBlock(elements=[
                ButtonElement(text="Создать канал", style='primary', action_id='create_channel')
            ], block_id='control_buttons').to_dict()
        ]
    # otherwise, we first authenticate
    else:
        home_view_init['blocks'] += [
            SectionBlock(text=text +
                              f'Для работы в панели необходимо пройти авторизацию в приложении по ссылке:{request.host_url + "auth"}',
                         block_id='need_authorization_block').to_dict()
        ]
    config.bot_client.views_publish(user_id=user_id_opened, view=home_view_init)
