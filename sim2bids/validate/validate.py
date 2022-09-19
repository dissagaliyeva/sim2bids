import os

import pandas as pd
import panel as pn
from scipy.io import loadmat
import mat73
import scipy

import sim2bids.generate.subjects as subj
from sim2bids.app import app

RENAMED = []


def validate(unique_files, all_files, paths):
    to_rename = []

    for idx, file in enumerate(unique_files):
        if type(file) == pn.widgets.select.Select:
            name, value = file.name.replace('Specify ', ''), file.value
            ext = name.split('.')[-1]

            if value in ['weights', 'distances', *app.ACCEPTED[3:]]:
                to_rename.append(value)

                if verify_weights(name):
                    rename_files(name, value, paths)
            elif value == 'weights & nodes':
                result = verify_weights_nodes(name, all_files)

                if isinstance(result, bool):
                    pass
                elif isinstance(result, list):
                    extract_files(name, result[1], result[-1], all_files)

            # if the selection's value is "skip", remove the file from input folder
            elif value == 'skip':
                remove_files(name, paths)
            elif value == 'map':
                if ext in ['csv', 'dat', 'txt']:
                    rename_files(name, 'map', paths)
            elif value == 'ts':
                if ext in ['csv', 'dat', 'txt']:
                    rename_files(name, 'ts', paths)

    if len(to_rename) == len(RENAMED):
        pn.state.notifications.success('Renamed all files!')

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
                os.rename(file, file.replace(name, new_ext + '.txt'))
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