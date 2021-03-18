###
# A simple tree building algorithm. Takes in paths and returns a tree structure
###
docs = [
    {
        'path': 'a',
        'content': '1'
    },
    {
        'path': 'a/b',
        'content': '12'
    },
    {
        'path': 'a/b/d',
        'content': '124'
    },
    {
        'path': 'c',
        'content': 3
    }
]


def build_tree(doc, iter=0):
    children = []
    print(iter, doc['path'])
    for d in docs:
        print('loop', iter, d['path'])
        if d['path'].startswith(doc['path']) and d['path'] != doc['path'] and '/' not in d['path'][
                                                                                         len(doc['path']) + 1:]:
            print('append', iter, d['path'])
            children.append(build_tree(d, iter + 1))
    data = {
        'path': doc['path'],
        'content': doc['content'],
        'children': children
    }
    return data
