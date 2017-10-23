# import python_jsonschema_objects as pjs
# import requests
# #
# # person_schema = {
# #     "title": "Person Schema",
# #     "type": "object",
# #     "properties": {
# #         "firstName": {
# #             "type": "string"
# #         },
# #         "lastName": {
# #             "type": "string"
# #         },
# #         "age": {
# #             "description": "Age in years",
# #             "type": "integer",
# #             "minimum": 0
# #         },
# #         "dogs": {
# #             "type": "array",
# #             "items": {"type": "string"},
# #             "maxItems": 4
# #         },
# #         "address": {
# #             "type": "object",
# #             "properties": {
# #                 "street": {"type": "string"},
# #                 "city": {"type": "string"},
# #                 "state": {"type": "string"}
# #                 },
# #             "required":["street", "city"]
# #             },
# #         "gender": {
# #             "type": "string",
# #             "enum": ["male", "female"]
# #         },
# #         "deceased": {
# #             "enum": ["yes", "no", 1, 0, "true", "false"]
# #             }
# #     },
# #     "required": ["firstName", "lastName"]
# # }
# from flask import request
#
rgb_schema = {
    "title": "RGB Colour",
    "type": "object",
    "properties": {
        "Red": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
        },
        "Green": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
            },
        "Blue": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255
        }
    },
    # "required": ["Red", "Green", "Blue"]
}
rgb_schema_gen = {
  "title": "RGB Colour",
  "$schema": "http://json-schema.org/draft-06/schema#",
  "definitions": {},
  "id": "http://example.com/example.json",
  "properties": {
    "Blue": {
      "default": 103,
      "description": "An explanation about the purpose of this instance.",
      "examples": [
        "103"
      ],
      "id": "/properties/blue",
      "title": "The blue schema.",
      "type": "integer"
    },
    "green": {
      "default": 102,
      "description": "An explanation about the purpose of this instance.",
      "examples": [
        "102"
      ],
      "id": "/properties/green",
      "title": "The green schema.",
      "type": "integer"
    },
    "Red": {
      "default": 101,
      "description": "An explanation about the purpose of this instance.",
      "examples": [
        "101"
      ],
      "id": "/properties/red",
      "title": "The red schema.",
      "type": "integer"
    }
  },
  "type": "object"
}
iss_location_schema = {
  "title": "ISS Location",
  "$schema": "http://json-schema.org/draft-06/schema#",
  "definitions": {},
  "id": "http://example.com/example.json",
  "properties": {
    "iss_position": {
      "id": "/properties/iss_position",
      "properties": {
        "latitude": {
          "default": "-16.7865",
          "description": "An explanation about the purpose of this instance.",
          "examples": [
            "-16.7865"
          ],
          "id": "/properties/iss_position/properties/latitude",
          "title": "The latitude schema.",
          "type": "string"
        },
        "longitude": {
          "default": "-170.2259",
          "description": "An explanation about the purpose of this instance.",
          "examples": [
            "-170.2259"
          ],
          "id": "/properties/iss_position/properties/longitude",
          "title": "The longitude schema.",
          "type": "string"
        }
      },
      "type": "object"
    },
    "message": {
      "default": "success",
      "description": "An explanation about the purpose of this instance.",
      "examples": [
        "success"
      ],
      "id": "/properties/message",
      "title": "The message schema.",
      "type": "string"
    },
    "timestamp": {
      "default": 1508313950,
      "description": "An explanation about the purpose of this instance.",
      "examples": [
        "1508313950"
      ],
      "id": "/properties/timestamp",
      "title": "The timestamp schema.",
      "type": "integer"
    }
  },
  "type": "object"
}
#
#
# def ObjectFromSchemaFactory(schema):
#     builder = pjs.ObjectBuilder(schema)
#     clasessRepository = builder.build_classes()
#     return clasessRepository
#
# print rgb_schema_gen['title']
# # print(dir(ns))
# # RgbColour = ns.RgbColour
# # ISSLocation = ns.IssLocation
# #
# # # james = Person(firstName = 'James', lastName = 'Bond')
# # #
# # # james.gender = 'male'
# # # james.age = 50
# # #
# # # james.address = {'street': 'Ulica', 'city': 'London'}
# # #
# # # print james.serialize()
# # #
# # # for param in james:
# # #     print param, type(param)
# # colour = RgbColour(red=101, green=102, blue=103)
# # # colour.red = 101
# #
# #
# # print colour.serialize()
# # new_location = ISSLocation(timestamp=24412141)
# # new_location.message = 'yay'
# # new_location.iss_position = {"latitude": "50", "longitude": "15"}
# # for field in new_location.as_dict():
# #     print field
# #
# # response = requests.get('http://api.open-notify.org/iss-now.json')
# # print response.content
# #
#
# import inspect

from jinja2 import Environment, FileSystemLoader
env = Environment(
    loader=FileSystemLoader('./')
)

# def foo(bar):
#     bar += 10
#     return bar

# lines = inspect.getsourcelines(foo)
template  = env.get_template('service_template.py')
# print template.render(input = 'RGB', output = 'rgb', arg1 = 'input', arg2 = 'output', route='index')

# print ''.join(lines[0])

def main(input_schema, output_schema):
    load_properties(input_schema, output_schema)
    matched = match_fields(input_schema, output_schema)
    print matched
    generate_code(input_schema, output_schema, matched)

def load_properties(input_schema, output_schema):
    if input_schema['properties']:
        print 'Input properties: ', input_schema['properties'].keys()
    else:
        print 'Input properties: ', input_schema.keys()

    if output_schema['properties']:
        print 'Output properties: ', output_schema['properties'].keys()
    else:
        print 'Output properties: ', output_schema.keys()

def match_fields(input_schema, output_schema):
    # Case sensitive
    matched = []
    for field in output_schema['properties'].keys():
        if field in input_schema['properties'].keys():
            #Should validate JSON Schema
            matched.append(field)
    return matched

def generate_code(input_schema, output_schema, matched_fields):
    inp = input_schema['title'].replace(' ','')
    out = output_schema['title'].replace(' ','')
    print template.render(input_format = inp
                        ,output_format = out
                        ,matched = matched_fields)

if __name__ == '__main__':
    main(rgb_schema, rgb_schema_gen)
