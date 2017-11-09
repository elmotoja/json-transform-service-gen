from flask import Flask, url_for, request, jsonify
import json

services = Flask(__name__)


@services.route('/')
def main():
    services.logger.warning('TEST!TEST!TEST')
    return jsonify(str(request))

@services.route('/RGB/', methods = ['POST', 'GET'])
def rgb():
    services.logger.warning('TEST!TEST!TEST')
    return str(request.get_json())

@services.route('/RGBColourtoRGBColour', methods = ['GET', 'POST'])
def RGBColourtoRGBColour():
    JSON_input = request.get_json()
    JSON_output = dict()

    JSON_output['Blue'] = JSON_input['Blue']

    JSON_output['Red'] = JSON_input['Red']

    return json.dumps(JSON_output)

if __name__ == '__main__':
    services.run(debug=True)
