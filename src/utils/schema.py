import json
# from ..process_dict import process_dict
from dictquery import DictQuery as dq
from operator import itemgetter


class Schema:
    def __init__(self, dictionary, slice=None):
        self._SCHEMA = dictionary
        if slice:
            self._PROCESSED = self._process(self._SCHEMA[slice])
        else:
            self._PROCESSED = self._process(self._SCHEMA)

    def __str__(self):
        return str(self._SCHEMA)

    def __getitem__(self, item):
        for record in self._PROCESSED:
            if record[0] == item:
                return record[1]
        raise KeyError(f'{item}')

    # def _load_schema_from_file(self, path_to_schema):
    #     with open(path_to_schema, 'r') as inFile:
    #         self._SCHEMA = json.loads(inFile.read())
    #         self._PROCESSED = self._process(self._SCHEMA['properties'])

    def load_schemas_from_url(self, input_url, output_url):
        raise NotImplementedError('Function not implemented yet!')

    def keys(self):
        return [key[0] for key in self._PROCESSED]

    def value(self, key):
        for item in self._PROCESSED:
            if item[0] == key:
                return item[1]

    def path(self, key, *, root=None) -> list:
        paths = self._PROCESSED
        if root:
            paths = [path for path in self._PROCESSED if root in path[2]]
        for item in paths:
            if item[0] == key:
                return item[2]

    def as_dict(self) -> dict:
        return self._SCHEMA

    def _process(self, dictionary):
        pre_processed = list()
        for item in self._process_dict(dictionary):
            if item[0] in ('type', 'minimum', 'maximum', 'title', 'id',
                           'description', 'examples', 'default', 'enum', 'required'):
                continue
            else:
                pre_processed.append(item)
        # remove duplicated paths
        processed = list()
        for record in pre_processed:
            # compare values under key in preprocessed dict and original
            if record[1] == dq(dictionary).get('/'.join(record[2])):
                processed.append(record)
            else:
                # remove record from list
                continue
        return sorted(processed, key=lambda t: len(t[2]))

    def _process_dict(self, d):
        for key, value in self._rec(d):
            for path in self._find_in_obj(d, key):
                yield (key, value, path)

    def _rec(self, dictionary):
        for key, value in dictionary.items():
            if type(value) is dict:
                yield key, value
                yield from self._rec(value)
            else:
                yield key, value

    def _find_in_obj(self, obj, condition, path=None):
        if path is None:
            path = []

        # In case this is a dictionary
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = list(path)
                new_path.append(key)
                for result in self._find_in_obj(value, condition, path=new_path):
                    yield result

                if condition == key:
                    new_path = list(path)
                    new_path.append(key)
                    yield new_path

if __name__ == "__main__":
    with open('../../schema/air_temperature', 'r') as inFile:
        schema = Schema(json.loads(inFile.read()), 'properties')

    # print(schema)
    # print(schema.keys())
    # print(schema._PROCESSED)
    # for t in schema._PROCESSED:
    #     print(t[2])
    print(schema.path('value', root='wind'))
    # print(schema.as_dict()['test'])

