import os

import numpy as np
import pandas as pd
import panel as pn
from scipy.io import loadmat
import mat73
import scipy

import sim2bids.generate.subjects as subj
from sim2bids.convert import convert
from sim2bids.app import app, utils

RENAMED = []


def filter(contents, files=None):
    if files is None:
        files = []

        for content in contents:
            if not subj.accepted(content):
                match = subj.find_matches([content])
                if len(match) > 0:
                    files.append(content.replace(match[0], '').replace('_', ''))
                else:
                    files.append(content)

        return list(set(files))

    # else get paths to files
    paths = []

    for content in contents:
        for file in files:
            if file in content:
                paths.append(content)

    return paths


def validate(unique_files, paths, input_path, input_files):
    for idx, file in enumerate(unique_files):
        if type(file) == pn.widgets.select.Select:
            name, value = file.name.replace('Specify ', ''), file.value
            ext = name.split('.')[-1]

            if value == 'weights':
                rename_weights(name, ext, paths, input_path, input_files)
            elif value == 'skip':
                remove_files(name, paths)
            else:
                rename_files(name, value, paths)

    pn.state.notifications.success('Preprocessing finished!')


def rename_weights(name, ext, paths, input_path, input_files):
    """
    This function checks if weights file already exists. If not, it creates
    a new weights file. Otherwise, checks against the existing weights,
    if the two weights file are equal, then saves only one copy. Otherwise,
    saves the new file with the extension used in the file.

    :param name:
    :param paths:
    :return:
    """
    files = get_files(paths, name, 'weights.txt', search1dir=True)
    open_file = lambda x: pd.read_csv(x, header=None, sep=subj.find_separator(x)).values

    # read the new file
    if ext in ['txt', 'dat', 'csv', 'tsv']:
        if len(files) > 1:
            f1, f2 = open_file(files[0]), open_file(files[1])

            # check if two files are different
            if not np.array_equal(f1, f2):
                for f in get_files(utils.get_content(input_path, input_files), name, 'weights'):
                    if 'weights' in f:
                        try:
                            os.rename(f, f.replace('weights.txt', f'weights_SCnotthrAn.txt'))
                        except FileExistsError:
                            return
                    else:
                        try:
                            os.rename(f, f.replace(name, f'weights_{name}'))
                        except FileExistsError:
                            return
        else:
            rename_files(name, 'weights', paths=paths)


def get_files(paths, file_name, constraint, search1dir=False):
    files, dir_name = [], os.path.dirname(paths[0])

    if search1dir:
        paths = [os.path.join(dir_name, f) for f in os.listdir(dir_name)]

    for path in paths:
        if file_name in path or constraint in path:
            files.append(path)

    return files


def verify_weights(name):
    ext = get_ext(name)

    if ext not in ['txt', 'csv']:
        pn.state.notifications.error('Weights should be in CSV, TXT format. '
                                     'Please double-check your selection')
        return False

    return True


def verify_weights_nodes(name, all_files):
    ext = get_ext(name)

    if ext == 'mat':
        mat, cols = open_mat(get_file(all_files, name))

        if 'sc' not in [x.lower() for x in cols]:
            pn.state.notifications.error('Weights are not found in MATLAB file. Please double-check your selection')
            return False
        else:
            if 'ids' in cols:
                return [True, mat, ['sc', 'ids']]


def extract_files(ext, mat, cols, paths):
    # check if the structure is multi-file in one folder
    matches = subj.find_matches([os.path.basename(x) for x in paths])
    base = os.path.basename(paths[0])
    og_path = paths[0].replace(base, '')

    for match in matches:
        for path in paths:
            if os.path.basename(path).startswith(match) and path.endswith(ext):
                mat[cols[0]].tofile(os.path.join(og_path, f'{match}_weights.txt'), sep=' ')
                pd.DataFrame(get_nodes(mat[cols[-1]])).to_csv(os.path.join(og_path, f'{match}_nodes.txt'),
                                                              header=None, index=None)
                # delete file
                os.remove(path)


def get_nodes(arr: list) -> list:
    all_nodes = []

    for node in arr:
        split = [x for x in node[0].split(' ') if x.startswith('ctx')]
        if len(split) > 0:
            all_nodes.append(split[0].replace('ctx', '').replace('-', '_').strip('-_/?.!,'))

    return all_nodes


def rename_files(name, new_ext, paths):
    global RENAMED
    new_ext = new_ext.replace('.', '').lower()

    for file in paths:
        if file.endswith(name):
            if file.endswith('txt') or file.endswith('csv') or file.endswith('dat'):
                p = os.path.dirname(file)
                if new_ext == 'weights' and 'weights.txt' in os.listdir(p):
                    os.rename(file, os.path.join(p, f'weights_{name}'))
                    os.rename(os.path.join(p, 'weights.txt'), os.path.join(p, 'weights_SCnotthrAn.txt'))
                else:
                    if name.lower() == new_ext.lower():
                        return

                    try:
                        # os.rename(file, file.replace(name, f'{name.replace("." + ext, "")}_{new_ext}' + '.txt'))
                        os.rename(file, file.replace(name, f'{new_ext}' + '.txt'))
                    except FileExistsError:
                        pn.state.notifications.error(f'File {new_ext} already exists!')
                    else:
                        RENAMED.append(file)
            elif file.endswith('mat'):
                pass


def get_file(files, end):
    for file in files:
        if file.endswith(end):
            return file


def get_ext(file):
    return os.path.basename(file).split('.')[-1]


def open_mat(file):
    try:
        mat = loadmat(file, squeeze_me=True)
    except NotImplementedError:
        mat = mat73.loadmat(file)
    except scipy.io.matlab._miobase.MatReadError:
        return

    return mat, find_mat_array(mat)


def find_mat_array(mat):
    data = []

    for k, v in mat.items():
        if type(v) not in [bytes, str, list]:
            data.append(k)

    return data


def remove_files(name, all_files):
    for file in all_files:
        if file.endswith(name):
            os.remove(file)

def get_extensions(files, ids=None):
    to_rename = []

    if ids is not None:
        files = [x for x in list(set([remove_id(x, ids) for x in files])) if x is not None]

    for file in files:
        found = False
        for acc in app.ACCEPTED:
            if file.lower().startswith(acc.lower()):
                found = True

        if not found:
            to_rename.append(file)

    return list(set(to_rename))


def remove_id(file, ids):
    for id_ in ids:
        if file.startswith(id_):
            return file.replace(id_, '').strip(',.\\/_;!?-')