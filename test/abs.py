import dpath.util


test = {
     "title": "Person Schema",
     "type": "object",
     "properties": {
        "Someone":{
         "firstName": {
             "type": "string"
         },
        "lastName": {
             "type": "string"
         }
         },
         "address": {
             "type": "object",
             "properties": {
                 "street": {"type": "string"},
                 "city": {"type": "string"},
                 "state": {"type": "string"}
                 },
             "required":["street", "city"]
             },
         "gender": {
             "type": "string",
             "enum": ["male", "female"]
         }
              },
     "required": ["firstName", "lastName"]
}

help(dpath.util.get)
# print(dpath.util.get(test, "/*/*/required"))
