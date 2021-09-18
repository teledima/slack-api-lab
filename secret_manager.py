def get_secret_data(secret_manager, project_id, secret_id, version_id):
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    return secret_manager.access_secret_version(request={"name": name}).payload.data.decode('UTF-8')

