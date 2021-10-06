from flask import Blueprint, render_template, request
from slack_sdk.oauth import AuthorizeUrlGenerator, RedirectUriPageRenderer
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from utils import set_document, encrypt_data
import config

auth_blueprint = Blueprint(name='auth_blueprint', import_name=__name__)


@auth_blueprint.route('/auth', methods=['GET'])
def auth():
    user_scopes = ['channels:write', 'channels:read', 'groups:write', 'groups:read']
    url_generator = AuthorizeUrlGenerator(client_id=config.client_id, user_scopes=user_scopes)
    return render_template('add_to_slack.html', url=url_generator.generate(state=''))


@auth_blueprint.route('/install', methods=['GET'])
def install_app():
    response = None
    finish_page = RedirectUriPageRenderer(install_path='/auth', redirect_uri_path='')
    # Get temporary code
    code = request.args.get('code')
    error = request.args.get('error')
    if code:
        # Exchange a temporary OAuth verifier code for an access token
        try:
            response = WebClient().oauth_v2_access(client_id=config.client_id,
                                                   client_secret=config.client_secret,
                                                   code=code).data
        except SlackApiError as slack_error:
            return finish_page.render_failure_page(reason=slack_error.response['error'])

    if response:
        nonce, encoded_data, tag = encrypt_data(key=config.encryption_key, data=bytes(response['authed_user']['access_token'], encoding='utf-8'))
        parsed_response = dict(app_id=response['app_id'],
                               user=dict(id=response['authed_user']['id'],
                                         scope=response['authed_user']['scope'],
                                         access_token=dict(nonce=list(nonce), encoded_data=list(encoded_data), tag=list(tag)),
                                         token_type=response['authed_user']['token_type']),
                               team=dict(id=response['team']['id'],
                                         name=response['team']['name']))

        set_document(db=config.db,
                     collection_id='authed_users',
                     document_id=response['authed_user']['id'],
                     content=parsed_response)
        return finish_page.render_success_page(app_id=response['app_id'], team_id=response['team']['id'])

    if error:
        return finish_page.render_failure_page(reason=error)
