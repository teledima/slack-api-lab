import os
import json

from secret_manager import get_secret_data
from google.cloud.secretmanager_v1 import SecretManagerServiceClient
from google.oauth2 import service_account

PROJECT_ID = 'api-slack-lab'
SECRET_MANAGER_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']


firebase_account_key = json.loads(os.getenv('FIREBASE_ACCOUNT_KEY'))
service_account_key = json.loads(os.getenv('SERVICE_ACCOUNT_KEY'))

secret_manager_cred = service_account.Credentials.from_service_account_info(service_account_key,
                                                                            scopes=SECRET_MANAGER_SCOPES)
secret_manager = SecretManagerServiceClient(credentials=secret_manager_cred)

client_id = get_secret_data(secret_manager=secret_manager,
                            project_id=PROJECT_ID, secret_id='client_id', version_id='latest')
client_secret = get_secret_data(secret_manager=secret_manager,
                                project_id=PROJECT_ID, secret_id='client_secret', version_id='latest')
