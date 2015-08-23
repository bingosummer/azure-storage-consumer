import os
import json
from cStringIO import StringIO
from flask import Flask, request, render_template, redirect, url_for, make_response
from azure.storage import BlobService
from azure import WindowsAzureMissingResourceError

import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

service_name = 'azurestorage'
vcap_services = json.loads(os.environ['VCAP_SERVICES'])
account_name = vcap_services[service_name][0]['credentials']['storage_account_name']
account_key = vcap_services[service_name][0]['credentials']['storage_account_key']
container_name = vcap_services[service_name][0]['credentials']['container_name']
blob_service = BlobService(account_name, account_key)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods= ['POST'])
def upload():
    file = request.files['file']
    app.logger.info('uploading file ' + file.filename)
    blob_service.put_block_blob_from_file(
        container_name,
        file.filename,
        file,
        max_connections=5
    )
    msg = '{0} is uploaded'.format(file.filename)
    return render_template("index.html", msg=msg)

@app.route('/download', methods= ['GET'])
def download():
    filename = request.args.get('filename')
    stream = StringIO()
    try:
        app.logger.info('downloading file ' + filename)
        blob_service.get_blob_to_file(
            container_name,
            filename,
            stream,
            max_connections=5
        )
    except WindowsAzureMissingResourceError as e:
        msg = '{0} not found'.format(filename)
        app.logger.debug(msg)
        return render_template("index.html", msg=msg)
    contents = stream.getvalue()
    response = make_response(contents)
    response.headers["Content-Type"] = "application/octet-stream"
    response.headers["Content-Disposition"] = "attachment; filename="+filename
    return response


port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    handler = RotatingFileHandler('demo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=int(port), debug=True)
