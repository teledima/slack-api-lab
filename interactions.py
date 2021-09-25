import json
from flask import Blueprint, request, make_response, jsonify
from slack_sdk import WebClient
from slack_sdk.models.blocks import PlainTextObject, SectionBlock, ActionsBlock, ButtonElement
from slack_sdk.models.messages import ObjectLink
from slack_sdk.errors import SlackApiError
import config
from datetime import datetime as dt
from utils import get_view, get_document

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_endpoint():
    payload = json.loads(request.form['payload'])
    if payload['type'] == 'block_actions':
        for action in payload['actions']:
            if action['action_id'] == 'channel_select_action':
                channel_selection_handler(view=payload['view'],
                                          selected_user=payload['user']['id'],
                                          selected_channel=action['selected_channel'])
            elif action['action_id'] == 'create_channel':
                pass
            elif action['action_id'] == 'delete_channel':
                pass
            elif action['action_id'] == 'edit_channel_name':
                pass
    elif payload['type'] == 'view_submission':
        callback_id = payload['view']['callback_id']
        pass
    return make_response('', 200)


def channel_selection_handler(view, selected_user, selected_channel):
    user_doc = get_document(db=config.db, collection_id='authed_users', document_id=selected_user)
    channel_info = WebClient(token=user_doc['user']['access_token']).conversations_info(channel=selected_channel)
    if channel_info.data['ok']:
        channel_data = channel_info.data['channel']
        channel_name = ObjectLink(object_id=channel_data['id'], text=channel_data['name'])
        created_time = dt.fromtimestamp(int(channel_data['created'])).strftime('%H:%M:%S %Y-%m-%d')
        previous_names = ','.join(channel_data['previous_names'])
        topic = channel_data['topic']['value']
        purpose = channel_data['purpose']['value']
    else:
        raise SlackApiError(message='Error while getting channel info', response=channel_info)

    channel_info_block = SectionBlock(text=f'Название канала: {channel_name}\n'
                                           f'Дата создания: {created_time}\n'
                                           f'Предыдущие названия: {previous_names}\n'
                                           f'Тема канала: {topic}\n'
                                           f'Описание: {purpose}\n',
                                      block_id='channel_info_block').to_dict()
    view_blocks = view['blocks']

    # remove old channel info blocks
    [view_blocks.pop(id) for id, item in enumerate(view_blocks)
     if 'block_id' in item and item['block_id'] == 'channel_info_block']

    view_blocks.insert(-1, channel_info_block)

    home_view = get_view('views/home_init.json')
    home_view['blocks'] = view_blocks

    WebClient(token=config.bot_token).views_update(view=home_view, view_id=view['id'])
