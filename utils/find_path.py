def find_path(obj, condition, path=None):

    if path is None:
        path = []    

    # In case this is a list
    if isinstance(obj, list):
        for index, value in enumerate(obj):
            new_path = list(path)
            new_path.append(index)
            for result in find_path(value, condition, path=new_path):
                yield result 

    # In case this is a dictionary
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = list(path)
            new_path.append(key)
            for result in find_path(value, condition, path=new_path):
                yield result 

            if condition == key:
                new_path = list(path)
                new_path.append(key)
                yield new_path

if __name__ == "__main__":
    schem = {
    "title": "GiftBox",
    "type": "object",
    "properties": {
        "price": {
            "value": {
                "type": "integer"
            },
            "currency": {
                "type": "string"}
    },
    "something": {"type": "string"}
}
}
    print(list(find_path(schem['properties'], 'something')))