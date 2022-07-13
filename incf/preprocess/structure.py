import os
from pathlib import Path
from itertools import islice
from incf.convert import convert

space = '&emsp;'
branch = '&emsp;&emsp;'
tee = '&emsp;&emsp;|___'
last = '&emsp;&emsp;|___'


def get_current_output(dir_path, level: int = -1, limit_to_directories: bool = False,
                       length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure"""
    if not os.path.exists(dir_path):
        return ''

    struct = []

    dir_path = Path(dir_path)  # accept string coerceable to Path
    files = 0
    directories = 0

    def inner(dir_path: Path, prefix: str = '', level=-1):
        nonlocal files, directories
        if not level:
            return  # 0, stop iterating
        if limit_to_directories:
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
        else:
            contents = list(dir_path.iterdir())
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + path.name
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path, prefix=prefix + extension, level=level - 1)
            elif not limit_to_directories:
                yield prefix + pointer + path.name
                files += 1

    struct.append(dir_path.name)

    iterator = inner(dir_path, level=level)
    for line in islice(iterator, length_limit):
        struct.append(line)

    print(struct)
    return '<br>'.join(struct)


# def get_current_output(path, indentation=2):
#     tree = []
#
#     if os.path.exists(path) and len(os.listdir(path)) > 0:
#         for root, dirs, files in os.walk(path):
#             level = root.replace(path, '').count(os.sep)
#             indent = '&emsp;' * indentation * level
#             tree.append('{}{}/'.format(indent, os.path.basename(root)))
#         tree = '<br>'.join(tree)
#     return tree


def create_layout(subs=None, output='../output'):
    """
    Create folder structure according to BEP034 and passed `subs` parameter.

    :param output:
    :param subs:
    :return:
    """

    output = output.replace('.', '').replace('/', '')
    layout = create_sub(subs)
    layout = '&emsp;'.join(layout) if len(layout) > 1 else ''.join(layout)

    return f"""
    {output}/ <br>
        &emsp;|___ code <br>
        &emsp;|___ eq <br>
        &emsp;|___ param <br>
        &emsp;{layout}
        &emsp;|___ README <br>
        &emsp;|___ CHANGES <br>
        &emsp;|___ dataset_description.json <br>
        &emsp;|___ participants.tsv
    """


def create_sub(subs):
    # centers_found, wd_found, sid = False, False, None
    centers_found, wd_found, wd_count = False, False, 0

    struct = []

    # sub_struct = """|___ sub-{} <br>
    # &emsp;&emsp;&emsp;|___ net <br>
    # &emsp;&emsp;&emsp;|___ spatial <br>
    # &emsp;&emsp;&emsp;|___ ts <br>
    # """
    sep = '&emsp;'
    fold, file = sep * 2, sep * 4

    structure = ['|___ sub-{} <br>', fold + '|___ net <br>',
                 fold + '|___ spatial <br>', fold + '|___ ts <br>',
                 file + '|___ sub-{}_desc-{}_{}.{} <br>',
                 fold + '|___ coord <br>', file + '|___ desc-{}_{}.{} <br>']

    sid = convert.SID

    for k, v in subs.items():
        name, desc = subs[k]['name'], subs[k]['desc']

        if subs[k]['fname'] in ['weights.txt', 'tract_lengths.txt', 'tract_length.txt', 'distances.txt']:
            wd_count += 1

            if not wd_found:
                struct += [structure[0].format(sid), structure[1]]
                wd_found = True

            struct += [structure[4].format(sid, desc, name, 'json'),
                       structure[4].format(sid, desc, name, 'tsv')]

            if wd_count == 2:
                struct += [structure[2], structure[3]]

        if subs[k]['path'].endswith('.mat'):
            if not wd_found:
                struct += [structure[0].format(sid), structure[1], structure[2], structure[3]]
                wd_found = True

            struct += [structure[4].format(sid, desc, name, '.json'),
                       structure[4].format(sid, desc, name, '.tsv')]

        if subs[k]['fname'] in ['centres.txt', 'centers.txt']:
            centers_found = True
            struct += [structure[5], structure[6].format(desc, 'nodes', 'json'),
                       structure[6].format(desc, 'nodes', 'tsv'),
                       structure[6].format(desc, 'labels', 'json'),
                       structure[6].format(desc, 'labels', 'tsv')]

    # # TODO: verify correct consecutive order
    # # struct[0] = struct[0].format(SID)
    # # struct.append(['&emsp;&emsp;&emsp;|___ spatial <br>', '&emsp;&emsp;&emsp;|___ ts <br>'])
    #
    if not centers_found:
        struct.append('|___ coord <br>')

    return struct


def create_sub_folders(path):
    sub = os.path.join(path, f'sub-{SID}')
    net = os.path.join(sub, 'net')
    ts = os.path.join(sub, 'ts')
    spatial = os.path.join(sub, 'spatial')

    for file in [sub, net, ts, spatial]:
        if not os.path.exists(file):
            os.mkdir(file)


def check_folders(path):
    eq = os.path.join(path, 'eq')
    code = os.path.join(path, 'code')
    coord = os.path.join(path, 'coord')
    param = os.path.join(path, 'param')

    for p in [path, eq, code, coord, param]:
        if not os.path.exists(p):
            print(f'Creating folder `{os.path.basename(p)}`...')
            os.mkdir(p)

    read = os.path.join(path, 'README.txt')
    part = os.path.join(path, 'participants.tsv')
    desc = os.path.join(path, 'dataset_description.json')
    chgs = os.path.join(path, 'CHANGES.txt')

    for p in [read, part, desc, chgs]:
        if not os.path.exists(p):
            print(f'Creating file `{os.path.basename(p)}`...')
            Path(p).touch()
