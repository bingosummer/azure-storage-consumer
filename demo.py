import os
import json
from flask import Flask
from azure.storage import BlobService

app = Flask(__name__)

service_name = 'azurestorage'

@app.route('/')
def demo():
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    account_name = vcap_services[service_name][0]['credentials']['storage_account_name']
    account_key = vcap_services[service_name][0]['credentials']['storage_account_key']
    container_name = vcap_services[service_name][0]['credentials']['container_name']
    blob_service = BlobService(account_name, account_key)
    blob_service.put_block_blob_from_path(
        container_name,
        'image.png',
        'image.png',
        max_connections=5
    )
    return container_name

port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
