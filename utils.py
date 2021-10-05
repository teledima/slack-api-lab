import json
from Crypto.Cipher import AES
from errors import DecryptionError


def get_secret_data(secret_manager, project_id, secret_id, version_id):
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    return secret_manager.access_secret_version(request={"name": name}).payload.data.decode('UTF-8')


def get_view(file_path: str):
    with open(file=file_path, mode='r', encoding='utf-8') as view_file:
        return json.load(view_file)


def get_document(db, collection_id, document_id):
    document = db.collection(collection_id).document(document_id).get()
    if document.exists:
        return document.to_dict()
    return dict()


def set_document(db, collection_id, document_id, content):
    db.collection(collection_id).document(document_id).set(content)


def encrypt_data(key: bytes, data: bytes):
    aes_cipher = AES.new(key=key, mode=AES.MODE_EAX)
    encoded_data, tag = aes_cipher.encrypt_and_digest(plaintext=data)
    return aes_cipher.nonce, encoded_data, tag


def decrypt_token(key: bytes, nonce: bytes, encoded_data: bytes, tag: bytes):
    aes_cipher = AES.new(key=key, mode=AES.MODE_EAX, nonce=nonce)
    decoded_data = aes_cipher.decrypt(encoded_data)
    try:
        aes_cipher.verify(received_mac_tag=tag)
        return decoded_data
    except ValueError:
        raise DecryptionError('Error while verifying mac tag')
