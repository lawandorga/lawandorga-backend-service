def map_values(mapping: dict, values: dict):
    """
    Maps values to a new dict.
    @param mapping: might look like this:
    dict: {
        'first': 'a',
        'second': 'b',
        'third': 'x'
    }
    @param values: might look like this:
    values: {
        'a': 123,
        'b': 'letter',
        'c': 'whatever'
    }
    @return: then this function returns:
    {
        'first': 123,
        'second': 'letter'
    }
    """
    result = {}
    for key, item in mapping.items():
        if item in values:
            result[key] = values[item]
    return result
