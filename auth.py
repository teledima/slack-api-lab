from firebase_admin import firestore
from flask import Blueprint, render_template, request
from slack_sdk.oauth import AuthorizeUrlGenerator, RedirectUriPageRenderer
from slack_sdk import WebClient
import config

auth_blueprint = Blueprint(name='auth_blueprint', import_name=__name__)


@auth_blueprint.route('/auth', methods=['GET'])
def auth():

    url_generator = AuthorizeUrlGenerator(client_id=config.client_id,
                                          scopes=['chat:write'], user_scopes=['users:read'])
    return render_template('add_to_slack.html', url=url_generator.generate(state=''))


@auth_blueprint.route('/install', methods=['GET'])
def install_app():
    # Get temporary code
    code = request.args.get('code')
    if code:
        finish_page = RedirectUriPageRenderer(install_path='/auth', redirect_uri_path='')
        # Exchange a temporary OAuth verifier code for an access token
        response = WebClient().oauth_v2_access(client_id=config.client_id,
                                               client_secret=config.client_id,
                                               code=code).data
        if response['ok']:
            parsed_response = dict(app_id=response['app_id'],
                                   user=dict(id=response['authed_user']['id'],
                                             scope=response['authed_user']['scope'],
                                             access_token=response['authed_user']['access_token'],
                                             token_type=response['authed_user']['token_type']),
                                   team=dict(id=response['team']['id'],
                                             name=response['team']['name']))
            db = firestore.client().collection('authed_users')
            db.document(response['authed_user']['id']).set(parsed_response)
            return finish_page.render_success_page(app_id=response['app_id'], team_id=response['team']['id'])
        else:
            return finish_page.render_failure_page(reason=response['error'])
