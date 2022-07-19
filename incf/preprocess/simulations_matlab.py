import os

import mat73
import panel as pn
import scipy
import scipy.io.matlab._miobase
from scipy.io import loadmat

from incf.convert import convert


def save(subs, path):
    duration, fname = convert.DURATION, subs['fname']
    try:
        mat = loadmat(subs['path'], squeeze_me=True)
    except NotImplementedError:
        pn.state.notifications.info(f'File `{fname}` uses MATLAB version 7.3.', duration=duration)
        save_mat73(subs, path)
    except scipy.io.matlab._miobase.MatReadError:
        pn.state.notifications.error(f'File `{fname}` is empty! Aborting...', duration=duration)
    else:
        convert_mat(mat, subs, path)


def save_mat73(subs, path):
    mat = mat73.loadmat(subs['path'])
    convert_mat(mat, subs, path)


def convert_mat(mat, subs, path):
    name, duration, fname = subs['name'], convert.DURATION, subs['fname']
    sid, desc = subs['sid'], subs['desc']
    temp = 'sub-{}_desc-{}-{}.{}'
    data = find_mat_array(mat)

    if len(data) == 0:
        pn.state.notifications.error(f'File `{fname}` does not have any data input!', duration=duration)
    elif len(data) == 1:
        data = mat[data[0]]

        ts_path = os.path.join(path, f'sub-{sid}', 'ts')
        coord_json = os.path.join(path, 'coord', f'desc-{desc}_times.json')
        coord_tsv = os.path.join(path, 'coord', f'desc-{desc}_times.tsv')

        convert.create_sub_struct(path, subs)
        convert.to_tsv(os.path.join(ts_path, temp.format(sid, desc, name, 'tsv')), data)
        convert.to_json(os.path.join(ts_path, temp.format(sid, desc, name, 'json')), data.shape, '', 'simulations')
        convert.to_json(coord_json, data.shape, 'Time steps of the simulated time series.', 'wd')
        convert.to_tsv(coord_tsv)
    else:
        print(data)


def find_mat_array(mat):
    data = []

    for k, v in mat.items():
        if type(v) not in [bytes, str, list]:
            data.append(k)

    return data
