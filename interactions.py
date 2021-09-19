import json
from flask import Blueprint, request, make_response
from slack_sdk import WebClient
from slack_sdk.models.blocks import PlainTextObject, SectionBlock
from firebase_admin import firestore
import config
import datetime as dt

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)
db = firestore.client(config.firestore_app).collection('authed_users')


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_endpoint():
    payload = json.loads(request.form['payload'])
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

                presence_text = PlainTextObject(text=f'Акивность: {presence_response["presense"]}\n'
                                                     f'Онлайн: {presence_response["online"]}\n'
                                                     f'Количество подключений: {presence_response["connection_count"]}\n'
                                                     f'Последняя активность: {last_activity}').to_dict()

                presence_text_block = SectionBlock(text=presence_text).to_dict()

                with open('views/home.json', 'r', encoding='utf-8') as home_view_file:
                    home_view = json.load(home_view_file)

                home_view['blocks'].append(presence_text_block)
                WebClient(config.bot_token).views_update(view=home_view, view_id=payload['container']['view_id'])
    return make_response('', 200)
