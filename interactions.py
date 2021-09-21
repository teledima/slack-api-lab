import json
from flask import Blueprint, request, make_response
from slack_sdk import WebClient
from slack_sdk.models.blocks import PlainTextObject, SectionBlock, ActionsBlock, ButtonElement
from firebase_admin import firestore
import config
import datetime as dt
from utils import get_view

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)
db = firestore.client(config.firestore_app).collection('authed_users')


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_endpoint():
    payload = json.loads(request.form['payload'])
    send_invite_button = payload['view']['blocks'].pop()
    added_blocks = []
    for action in payload['actions']:
        if action['action_id'] == 'users_select-action':
            user_id = action['selected_user']
            user_doc = db.document(user_id).get()
            if user_doc.exists:
                user_doc_dict = user_doc.to_dict()
                presence_response = WebClient(user_doc_dict['user']['access_token']).users_getPresence(user=user_id)

                if 'last_activity' in presence_response:
                    unix_last_activity = presence_response['last_activity']
                    last_activity = dt.datetime.fromtimestamp(int(unix_last_activity)).strftime("%H:%M:%S %Y-%m-%d")
                else:
                    last_activity = 'нет данных о последней активности'

                presence_text = PlainTextObject(text=f'Акивность: {presence_response["presence"]}\n'
                                                     f'Онлайн: {presence_response["online"]}\n'
                                                     f'Количество подключений: {presence_response["connection_count"]}\n'
                                                     f'Последняя активность: {last_activity}').to_dict()

                presence_text_block = SectionBlock(text=presence_text).to_dict()
                buttons = ActionsBlock(elements=[
                    send_invite_button['elements'][0],
                    ButtonElement(text="Удалить пользователя", action_id='delete_user_action', style='danger').to_dict(),
                    ButtonElement(text='Изменить статус', action_id='set_user_status').to_dict()
                ]).to_dict()

                added_blocks = [presence_text_block, buttons]
            else:
                presence_text_block = SectionBlock(text='Не удалось получить информацию об активности для выбранного пользователя').to_dict()
                added_blocks = [presence_text_block, send_invite_button]

            home_view = get_view('views/home_init.json')
            home_view['blocks'] = payload['view']['blocks'] + added_blocks

            WebClient(config.bot_token).views_update(view=home_view, view_id=payload['container']['view_id'])
    return make_response('', 200)
