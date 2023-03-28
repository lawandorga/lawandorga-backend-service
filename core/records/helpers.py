def merge_attrs(attrs1, attrs2):
    all_attrs = list(attrs1.items()) + list(attrs2.items())
    attrs = {}
    for key, value in all_attrs:
        if key not in attrs:
            attrs[key] = value
            continue

        if not isinstance(value, list):
            value = [value]

        if not isinstance(attrs[key], list):
            attrs[key] = [attrs[key]]

        attrs[key] = attrs[key] + value

    return attrs
