import os
from pathlib import Path
from itertools import islice

space = '&emsp;'
branch = '&emsp;&emsp;'
tee = '&emsp;&emsp;|___'
last = '&emsp;&emsp;|___'


def get_current_output(dir_path, level: int = -1, limit_to_directories: bool = False,
                       length_limit: int = 1000) -> str:
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
    pass
