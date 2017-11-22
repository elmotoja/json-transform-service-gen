from six import iteritems

def path_to(key, document):
    """Find path to key in a nested document, return a list of steps"""
    return list(_path_to(key, document))

def _path_to(key, document, path=[]):
    """Find path to key in a nested document, yield a value"""
    if isinstance(document, list):
        for d in document:
            for result in _path_to(key, d):
                yield []

    if isinstance(document, dict):
        for k, v in iteritems(document):
            if k == key:
                path.append(k)
                yield path
            elif isinstance(v, dict):
                path.append(k)
                for result in _path_to(key, v, path=path):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    path.append(d)
                    for result in _path_to(key, d):
                        yield result

if __name__ == "__main__":
    test = {'a': {'b': {'c': {'d': 1}}}}

    print(path_to('d', test))
