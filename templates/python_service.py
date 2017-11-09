from flask import Flask, request
import json
{% for method in imports %}from transforms import {{method}}
{% endfor %}
import transforms
service = Flask(__name__)

@service.route('/{{input_format}}to{{output_format}}', methods = ['GET', 'POST'])
def {{input_format}}to{{output_format}}():
    JSON_input = request.get_json()
    JSON_output = dict()
    {% for match in filling %}
    JSON_output['{{match[1]}}'] = transforms.{{match[2]}}(JSON_input['{{match[0]}}'])
    {% endfor %}
    return json.dumps(JSON_output)

if __name__ == '__main__':
    service.run(port=0)
