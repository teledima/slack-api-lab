from flask import Blueprint, request
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
from slack_sdk.models.blocks import SectionBlock, UserSelectElement, ActionsBlock, ButtonElement
from firebase_admin import firestore
from utils import get_view

import config


event_blueprint = Blueprint('event_blueprint', import_name=__name__)
event_adapter = SlackEventAdapter(config.signing_secret, endpoint='/event-endpoint', server=event_blueprint)

db = firestore.client(config.firestore_app).collection('authed_users')


@event_adapter.on('app_home_opened')
def event_endpoint(event_data):
    home_view_init = get_view('views/home_init.json')

    user_id_opened = event_data['event']['user']
    user_doc = db.document(user_id_opened).get()

    token = user_doc.to_dict()['user']['access_token'] if user_doc.exists else config.bot_token
    user_info = WebClient(token=token).users_info(user=user_id_opened)
    is_admin = user_info['user']['is_admin'] or user_info['user']['is_owner']

    if user_doc.exists:
        if user_info['ok'] and is_admin:
            home_view_init['blocks'] += [
                SectionBlock(text='Добро пожаловать в панель администратора. '
                                  'Ниже вы можете выбрать пользователя для выполнения действий.').to_dict(),
                SectionBlock(text='Пользователь для просмотра активности', block_id='user_presence_select',
                             accessory=UserSelectElement(placeholder='Выберите пользователя', action_id='users_select-action')).to_dict(),
                ActionsBlock(block_id='send_invitation_block', elements=[
                    ButtonElement(text='Пригласить нового пользователя', action_id='send_invitation_action', style='primary')
                ]).to_dict(),
            ]
        else:
            if not user_info['ok']:
                home_view_init['blocks'] += [
                    SectionBlock(text=f'Произошла ошибка. Данные об ошибке: {user_info["error"]}').to_dict()
                ]
            else:
                home_view_init['blocks'] += [
                    SectionBlock(text=f'У вас недостаточно прав для просмотра страницы администратора').to_dict()
                ]
    else:
        home_view_init['blocks'] += [
            SectionBlock(text=f"Вы не выполнили авторизацию в приложении.\n"
                              f"Для прохождения авторизации перейдите по ссылке: {request.host_url + f'auth?is_admin={1 if is_admin else 0}'}").to_dict()
        ]

    WebClient(token=config.bot_token).views_publish(view=home_view_init, user_id=user_id_opened)
