from flask import Flask, request
import json
from transforms import USDtoPLN

import transforms
service = Flask(__name__)

@service.route('/USDPricetoPLNPrice', methods = ['GET', 'POST'])
def USDPricetoPLNPrice():
    JSON_input = request.get_json()
    # Validate input
    JSON_output = dict()
    
    JSON_output['PLN'] = transforms.USDtoPLN(JSON_input['USD'])

    # Validate output
    return json.dumps(JSON_output)


if __name__ == '__main__':
    service.run(port=0)