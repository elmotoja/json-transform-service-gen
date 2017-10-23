@services.route('/{{input_format}}to{{output_format}}', methods = ['GET', 'POST'])
def {{input_format}}to{{output_format}}():
    JSON_input = request.get_json()
    JSON_output = dict()
    {% for match in matched %}
    JSON_output['{{match}}'] = JSON_input['{{match}}']
    {% endfor %}
    return json.dumps(JSON_output)
