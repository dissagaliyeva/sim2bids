import os

import mat73
import panel as pn
import scipy
import scipy.io.matlab._miobase
from scipy.io import loadmat

from incf.convert import convert


def save(subs, folders, ses=None):
    duration, fname = convert.DURATION, subs['fname']
    try:
        mat = loadmat(subs['path'], squeeze_me=True)
    except NotImplementedError:
        pn.state.notifications.info(f'File `{fname}` uses MATLAB version 7.3.', duration=duration)
        save_mat73(subs, folders, ses=ses)
    except scipy.io.matlab._miobase.MatReadError:
        pn.state.notifications.error(f'File `{fname}` is empty! Aborting...', duration=duration)
    else:
        convert_mat(mat, subs, folders, ses=ses)


def save_mat73(subs, folders, ses):
    mat = mat73.loadmat(subs['path'])
    convert_mat(mat, subs, folders, ses=ses)


def convert_mat(mat, subs, folders, ses=None):
    name, duration, fname = subs['name'], convert.DURATION, subs['fname']
    sid, desc = subs['sid'], subs['desc']
    data = find_mat_array(mat)

    if len(data) == 0:
        pn.state.notifications.error(f'File `{fname}` does not have any data input!', duration=duration)
    elif len(data) == 1:
        data = mat[data[0]]
        ts_path = folders[-1]
        spatial_path = folders[2] if ses is None else folders[3]

        if 'fc' in name.lower():
            coord_json = os.path.join(spatial_path, f'{sid}_desc-{desc}_fc.json')
            coord_tsv = os.path.join(spatial_path, f'{sid}_desc-{desc}_fc.tsv')
        else:
            if ses is None:
                coord_json = os.path.join(ts_path, f'desc-{desc}_{name}.json')
                coord_tsv = os.path.join(ts_path, f'desc-{desc}_{name}.tsv')
            else:
                coord_json = os.path.join(ts_path, f'{sid}_desc-{desc}_{name}.json')
                coord_tsv = os.path.join(ts_path, f'{sid}_desc-{desc}_{name}.tsv')

        save_tsv_json(coord_tsv, data)
        save_tsv_json(coord_json, data, tsv=False)
    else:
        print('MATLAB weird files, `simulations_matlab.py` @51:', data)


def save_tsv_json(path, data, tsv=True, desc=None):
    desc = '' if desc is None else desc

    if tsv:
        convert.to_tsv(path, data)
    else:
        convert.to_json(path, data.shape, desc, 'ts')


def find_mat_array(mat):
    data = []

    for k, v in mat.items():
        if type(v) not in [bytes, str, list]:
            data.append(k)

    return data
