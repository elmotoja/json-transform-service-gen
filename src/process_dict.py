import logging
from collections import defaultdict

def process_dict(d):
    for key, value in _rec(d):
        for path in _find_in_obj(d, key):
            yield (key, value, path)


def _rec(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            # p.append(key)
            # logging.warning(str(p))
            yield key, value
            yield from _rec(value)
        else:
            # p.append(key)
            # logging.warning(str(p)+' 2')
            yield key, value


def _find_in_obj(obj, condition, path=None):
    if path is None:
        path = []

    # In case this is a dictionary
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = list(path)
            new_path.append(key)
            for result in _find_in_obj(value, condition, path=new_path):
                yield result

            if condition == key:
                new_path = list(path)
                new_path.append(key)
                yield new_path


def dfs(graph, start):
    visited, stack = set(), [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            stack.extend(graph[vertex] - visited)
    return visited


def nesteddict():
    return defaultdict(nesteddict())

if __name__ == "__main__":



    test = {'x': 0,
            'a': {'b': {'c': {'d': 1}}},
            'aa': {'d': 'beng'}
            }
    test2 = {"properties": {
            'x': 0,
            'a': {'b': {'c': {'d': 1}}},
            'aa': {'d': 'beng'}
            }
            }

    td = nesteddict()
    # for item in process_dict(test):
    #     print(item)
    # for item in _rec(test, list()):
    #     print(item)
    # for item in _rec(test, list()):
    #     print(item)
    # print(dfs(test2, 'properties'))
    print(td.keys())





