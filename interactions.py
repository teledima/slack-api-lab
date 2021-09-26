import json
from flask import Blueprint, request, make_response, jsonify
from slack_sdk import WebClient
from slack_sdk.models.blocks import PlainTextObject, SectionBlock, InputBlock, ButtonElement, ConfirmObject, PlainTextInputElement
from slack_sdk.models.messages import ObjectLink
from slack_sdk.errors import SlackApiError
import config
from datetime import datetime as dt
from utils import get_view, get_document

interaction_blueprint = Blueprint('interaction_blueprint', import_name=__name__)


@interaction_blueprint.route('/interaction-endpoint', methods=['POST'])
def interaction_endpoint():
    payload = json.loads(request.form['payload'])

    user_dor = get_document(
        db=config.db, collection_id='authed_users', document_id=payload['user']['id']
    )
    user_client = WebClient(token=user_dor['user']['access_token'])

    # handle interactions in blocks
    if payload['type'] == 'block_actions':
        for action in payload['actions']:
            selected_channel = payload['view']['state']['values']['channel_select_block']['channel_select_action']['selected_channel']
            if action['action_id'] == 'channel_select_action':
                channel_selection_handler(view=payload['view'],
                                          user_client=user_client,
                                          selected_channel=action['selected_channel'])
            elif action['action_id'] == 'create_channel':
                config.bot_client.views_open(trigger_id=payload['trigger_id'],
                                             view=channel_view_construct(type_view='create'))
            elif action['action_id'] == 'archive_channel':
                try:
                    user_client.conversations_archive(channel=selected_channel)
                except SlackApiError:
                    # if there is an error, then simply suppress the error
                    return make_response('', 200)

            elif action['action_id'] == 'edit_channel_name':
                channel_data = user_client.conversations_info(channel=selected_channel).data['channel']
                config.bot_client.views_open(trigger_id=payload['trigger_id'],
                                             view=channel_view_construct(type_view='update_name',
                                                                         initial_value=channel_data['name'],
                                                                         channel_id=channel_data['id']))
    # handle interaction in custom views
    elif payload['type'] == 'view_submission':
        callback_id = payload['view']['callback_id']
        selected_channel = payload['view']['private_metadata']
        channel_name = payload['view']['state']['values']['channel_name_input_block']['channel_name_input_action']['value']
        if callback_id == 'create_channel_callback':
            return channel_handler(action=user_client.conversations_create, name=channel_name, is_private=False)
        elif callback_id == 'change_channel_name_callback':
            return channel_handler(action=user_client.conversations_rename, channel=selected_channel, name=channel_name)

    return make_response('', 200)


def channel_selection_handler(view, user_client: WebClient, selected_channel):
    channel_data = user_client.conversations_info(channel=selected_channel).data['channel']
    channel_name = ObjectLink(object_id=channel_data['id'], text=channel_data['name'])
    created_time = dt.fromtimestamp(int(channel_data['created'])).strftime('%H:%M:%S %Y-%m-%d')
    previous_names = ','.join(channel_data['previous_names'])
    topic = channel_data['topic']['value']
    purpose = channel_data['purpose']['value']

    channel_info_block = SectionBlock(text=f'Название канала: {channel_name}\n'
                                           f'Дата создания: {created_time}\n'
                                           f'Предыдущие названия: {previous_names}\n'
                                           f'Тема канала: {topic}\n'
                                           f'Описание: {purpose}\n',
                                      block_id='channel_info_block').to_dict()
    view_blocks = view['blocks']

    # remove old channel info blocks
    [view_blocks.pop(id) for id, item in enumerate(view_blocks)
     if ('block_id' in item and item['block_id'] == 'channel_info_block')]

    # find old delete and edit buttons
    if 'elements' in view_blocks[-1] and \
       'block_id' in view_blocks[-1] and view_blocks[-1]['block_id'] == 'control_buttons':

        delete_element_id = [id for id, item in enumerate(view_blocks[-1]['elements'])
                             if item['action_id'] == 'archive_channel']

    # insert channel info before control buttons
    view_blocks.insert(-1, channel_info_block)

    delete_text = f'Вы действительно хотите архивировать канал {channel_name}?'
    # if id exist then update
    if delete_element_id:
        view_blocks[-1]['elements'][delete_element_id.pop()]['confirm']['text']['text'] = delete_text
    # else insert
    else:
        # insert delete and change buttons
        view_blocks[-1]['elements'] += [
            ButtonElement(text="Архивировать канал", style='danger', action_id='archive_channel',
                          confirm=ConfirmObject(title='Архивирование канала',
                                                text=delete_text,
                                                deny='Нет, я передумал', confirm='Да',
                                                style='danger')).to_dict(),
            ButtonElement(text="Изменить название канала", action_id='edit_channel_name').to_dict()
        ]

    home_view = get_view('views/home_init.json')
    home_view['blocks'] = view_blocks

    config.bot_client.views_update(view=home_view, view_id=view['id'])


def channel_handler(action, **kwargs):
    try:
        action(**kwargs)
        return make_response('', 200)
    except SlackApiError as slack_api_error:
        error_text = 'Произошла ошибка при создании канала: {error_description}'
        if slack_api_error.response['error'] == 'invalid_name_specials':
            error_text = error_text.format(
                error_description='имя содержит недопустимые спец.знаки или символы верхнего регистра')
        elif slack_api_error.response['error'] == 'invalid_name_punctuation':
            error_text = error_text.format(error_description='имя содержит только знаки пунктуации')
        elif slack_api_error.response['error'] == 'name_taken':
            error_text = error_text.format(error_description='канал с таким именем уже существует')
        else:
            error_text = error_text.format(error_description=slack_api_error.response['error'])

        error_response = dict(response_action='errors',
                              errors=dict(channel_name_input_block=error_text))
        return jsonify(error_response), 200


def channel_view_construct(type_view, initial_value=None, channel_id=None):
    view_init = get_view('views/create_channel_view.json')

    input_block = InputBlock(
        block_id='channel_name_input_block', label='Название канала',
        element=PlainTextInputElement(action_id='channel_name_input_action',
                                      max_length=80,
                                      initial_value=initial_value)).to_dict()

    if type_view == 'create':
        view_init['callback_id'] = 'create_channel_callback'
        view_init['title'] = PlainTextObject(text='Создание канала').to_dict()
        view_init['submit'] = PlainTextObject(text='Создать канал').to_dict()
        view_init['close'] = PlainTextObject(text='Отменить').to_dict()
        view_init['blocks'].append(input_block)
    elif type_view == 'update_name':
        view_init['callback_id'] = 'change_channel_name_callback'
        view_init['title'] = PlainTextObject(text='Редактирование канала').to_dict()
        view_init['submit'] = PlainTextObject(text='Изменить название').to_dict()
        view_init['close'] = PlainTextObject(text='Отменить').to_dict()
        # set channel id to metadata because we can not read parent view while submission
        view_init['private_metadata'] = channel_id
        view_init['blocks'].append(input_block)
    else:
        return None

    return view_init
