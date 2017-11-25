from flask import Flask, request
import json
{% for method in imports %}from transforms import {{method}}
{% endfor %}
import transforms
service = Flask(__name__)

@service.route('/{{input_format}}to{{output_format}}', methods = ['GET', 'POST'])
def {{input_format}}to{{output_format}}():
    JSON_input = request.get_json()
    # Validate input
    JSON_output = dict()
    {% for match in filling %}
    JSON_output{%for step in match[0]%}['{{step}}']{% endfor %} = transforms.{{match[2]}}(JSON_input{%for step in match[1]%}['{{step}}']{% endfor %}){% endfor %}

    # Validate output
    return json.dumps(JSON_output)


if __name__ == '__main__':
    service.run(port=0)
