def merge_attrs(attrs1, attrs2):
    all_attrs = list(attrs1.items()) + list(attrs2.items())
    attrs = {}
    for key, value in all_attrs:
        if key in attrs:
            if isinstance(value, list):
                attrs[key] = attrs[key] + value
            else:
                attrs[key] = [attrs[key], value]
        else:
            attrs[key] = value
    return attrs
