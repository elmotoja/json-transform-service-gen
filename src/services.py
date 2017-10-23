from flask import Flask, url_for, request
import json
services = Flask(__name__)

@services.route('/')
def main():
    return '<h1>"Services main Page!"</h1>'

@services.route('/RGB/', methods = ['POST', 'GET'])
def rgb():
    return str(request.get_json())

@services.route('/RGBColourtoRGBColour', methods = ['GET', 'POST'])
def RGBColourtoRGBColour():
    JSON_input = request.get_json()
    JSON_output = dict()

    JSON_output['Blue'] = JSON_input['Blue']

    JSON_output['Red'] = JSON_input['Red']

    return json.dumps(JSON_output)

if __name__ == '__main__':
    services.run()
