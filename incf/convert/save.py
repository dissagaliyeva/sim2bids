import json
import os
from collections import OrderedDict

import pandas as pd

from incf.app import app
from incf.generate import subjects
import incf.templates.templates as temp

# define naming appentions
DEFAULT_TEMPLATE = '{}_desc-{}_{}.{}'
COORD_TEMPLATE = 'desc-{}_{}.{}'
IGNORE_CENTRE = False


def save(sub, folders, ses=None, name=None):
    """

    :param sub:
    :param folders:
    :param ses:
    :param name:
    :return:
    """
    global IGNORE_CENTRE

    print('Passed in subject file:', sub)

    if IGNORE_CENTRE and name == 'centres':
        return

    # read file contents
    file = open_file(sub['path'], subjects.find_separator(sub['path']))

    # get folder location for weights and distances
    if name == 'wd':
        # set appropriate output path
        if ses is None:
            folder = folders[1]
        else:
            folder = folders[2]

        # save contents
        desc = temp.weights if 'weights' in sub['name'] else temp.distances
        save_files(sub, folder, file, desc=desc, ftype='wd')

    # get folder location for centres
    if name == 'centres':
        # check if all centres are of the same content
        if check_centres():
            IGNORE_CENTRE = True

            folder = os.path.join(app.OUTPUT, 'coord')

            # pass values to save json file
            save_files(sub, folder, file, type='coord', centres=True, desc=temp.centres['multi-same'])
        else:
            desc = temp.centres['multi-unique'] if app.MULTI_INPUT else temp.centres['single']

            if ses is not None:
                folder = folders[4]
            elif app.MULTI_INPUT and ses is None:
                folder = folders[3]
            else:
                folder = os.path.join(app.OUTPUT, 'coord')

            # save files
            save_files(sub, folder, file, type='default', centres=True, desc=desc)


def save_files(sub, folder, content, type='default', centres=False, desc=None, ftype='centres'):
    """

    :param sub:
    :param folder:
    :param content:
    :param type:
    :param centres:
    :param desc:
    :param ftype:
    :return:
    """

    if type == 'default':
        json_file = os.path.join(folder, DEFAULT_TEMPLATE.format(sub['sid'], sub['desc'], sub['name'], 'json'))
        tsv_file = json_file.replace('json', 'tsv')
    else:
        json_file = os.path.join(folder, COORD_TEMPLATE.format(sub['desc'], sub['name'], 'json'))
        tsv_file = json_file.replace('json', 'tsv')

    print('JSON file:', json_file)
    print('TSV file:', tsv_file)

    # Save 'centres.txt' as 'nodes.txt' and 'labels.txt'. This will require breaking the
    # 'centres.txt' file, the first column HAS TO BE labels, and the rest N dimensions
    # are nodes.
    if centres:
        # create names for nodes and labels
        # Since the usual structure leaves the name of the files as is,
        # we need to make sure we save 'nodes' and 'labels' appropriately.
        # If we didn't create these two values below, both labels and nodes
        # would be stored as 'sub-<ID>_desc-<label>_centres.txt', and the
        # content would only have nodes.
        labels = json_file.replace(sub['name'], 'labels')
        nodes = json_file.replace(sub['name'], 'nodes')

        # save labels to json and tsv
        to_json(labels, shape=[content.shape[0], 1], key='coord', desc=desc[0])
        to_tsv(labels.replace('json', 'tsv'), content[0])

        # save nodes to json and tsv
        to_json(nodes, shape=content.shape, key='coord', desc=desc[1])
        to_tsv(nodes.replace('json', 'tsv'), content[1:])
    else:
        # otherwise, save files as usual
        to_json(json_file, shape=content.shape, key=ftype, desc=desc)
        to_tsv(tsv_file, content)


def check_centres():
    """

    :return:
    """
    # get all centres files
    centres = get_specific('centres')
    file = open_file(centres[0], subjects.find_separator(centres[0]))

    same = {}

    # iterate over centres
    for centre in centres[1:]:
        same.update(file == open_file(centre, subjects.find_separator(centre)))

    if len(same) == 1:
        if bool(same):
            return True
        return False
    return False


def get_specific(filetype: str) -> list:
    """
    Get all files that correspond to the filetype. For example,
    if filetype is equal to "areas", this function will return
    all files containing that keyword.

    :param filetype:
    :return:
    """

    content = []

    for file in app.ALL_FILES:
        if filetype in file:
            content.append(file)

    return content


def open_file(path: str, sep: str):
    """

    :param path:
    :param sep:
    :return:
    """

    ext = path.split('.')[-1]

    if ext in ['txt', 'csv', 'dat']:
        return open_text(path, sep)

    elif ext == 'mat':
        pass

    elif ext == 'h5':
        pass


def open_text(path, sep):
    """

    :param path:
    :param sep:
    :return:
    """
    try:
        f = pd.read_csv(path, sep=sep, header=None, index_col=False)
    except pd.errors.EmptyDataError:
        return ''
    except ValueError:
        return ''
    else:
        return f


def to_tsv(path, file, sep=None):
    """

    :param path:
    :param file:
    :param sep:
    :return:
    """
    params = {'sep': '\t', 'header': None, 'index': None}
    sep = sep if sep != '\n' else '\0'

    if isinstance(file, str) and sep is not None:
        pd.read_csv(file, index_col=None, header=None, sep=sep).to_csv(path, **params)
    else:
        try:
            pd.DataFrame(file).to_csv(path, **params)
        except ValueError:
            with open(file) as f:
                with open(path, 'w') as f2:
                    f2.write(f.read())


def to_json(path, shape, desc, key, coords=None, **kwargs):
    """

    :param path:
    :param shape:
    :param desc:
    :param key:
    :param coords:
    :param kwargs:
    :return:
    """
    inp = temp.required
    out = OrderedDict({x: '' for x in inp})

    if key != 'wd':
        struct = temp.struct[key]
        out.update({x: '' for x in struct['required']})
        out.update({x: '' for x in struct['recommend']})

    with open(path, 'w') as file:
        json.dump(temp.populate_dict(out, shape=shape, desc=desc, coords=coords, **kwargs), file)
