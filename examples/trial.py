import os
import pprint
import time
import json
import graphviz as gv
import sys

''' Build dict representing directory tree from start '''


def trace_path(start):
    count = 0
    layout = {}

    for root, dirs, files in os.walk(start):
        current_dict = layout
        path = root.split('/')
        if path[-1] == '':
            path.pop()
        if path[-1][0] == '.':
            print('hidden')
            # time.sleep(10)
            continue
        for folder in path:
            if folder == '':
                continue
            if folder not in current_dict:
                current_dict[folder] = {}

            current_dict = current_dict[folder]
        for di in dirs:
            if not di[0] == '.':
                current_dict[di] = {}
        for fi in files:
            if not fi[0] == '.':
                current_dict[fi] = None
        count += 1

    return layout


''' Write json data to file name '''


def write_to_file(file_name, data):
    with open(file_name, 'w') as fp:
        json.dump(data, fp)


''' Read from a json formatted file and return dict '''


def load_from_file(file_name):
    with open(file_name, 'r') as fp:
        return json.load(fp)


''' Create a render for a graph given a dict '''


def visualize(data, out_file):
    g = gv.Graph()
    queue = ['home']
    visited = set('home')
    g.node('home')
    prev = {}
    prev['home'] = None
    while queue:
        node = queue.pop()
        if node[0] == '.':
            print('hidden')
            continue
        for neighbor in traverse_to_dict(data, get_path(prev, node)):
            if neighbor not in visited:
                queue.append(neighbor)
                visited.add(neighbor)
                prev[neighbor] = node
                if check_encode(neighbor):
                    print(node)
                    g.node(neighbor)
                    g.edge(node, neighbor)

    g.save(out_file)
    os.system('dot -Tsvg -Ksfdp {0} > {1}'.format(out_file, out_file + '.svg'))
    os.system('rm {0}'.format(out_file))


''' Get the path from the root to the current node '''


def get_path(prev, node):
    current = node
    path = [current]
    while current:
        path.append(prev[current])
        current = prev[current]

    path.pop()

    return path[::-1]


''' Given a path return the proper dict '''


def traverse_to_dict(data, path):
    current_dict = data
    for node in path:
        if current_dict[node] is None:
            return current_dict
        current_dict = current_dict[node]

    return current_dict


'''  Check to make sure we can utf encode '''


def check_encode(to_check):
    try:
        to_check.encode('utf-8')
        return True
    except UnicodeEncodeError:
        return False


def main():
    default_file = 'graph.json'

    if len(sys.argv) < 2:
        print('Incorrect usage, arg path to trace is needed')
        exit()
    if len(sys.argv) < 3:
        print('Incorrect usage, output file name is also needed')
        exit()

    path_to_trace = sys.argv[1]
    if path_to_trace[0] != '/':
        print('Incorrect usage, arg path to trace has to be direct from root')
        exit()

    out_file = sys.argv[2]
    if '.' in out_file:
        print('Incorrect usave, file name cannot have . in it')
        exit()

    structure = trace_path(os.path.expanduser(path_to_trace))
    write_to_file(default_file, structure)

    data = load_from_file(default_file)

    visualize(data, out_file)


if __name__ == '__main__':
    main()
