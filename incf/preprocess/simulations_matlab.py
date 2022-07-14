import scipy
import scipy.io.matlab._miobase
from scipy.io import loadmat
import os
import mat73
import panel as pn
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
    print(mat)
    convert_mat(mat, subs, path)


def convert_mat(mat, subs, path):
    name, duration, fname = subs['name'], convert.DURATION, subs['fname']
    data = find_mat_array(mat)

    if len(data) == 0:
        pn.state.notifications.error(f'File `{fname}` does not have any data input!', duration=duration)
    elif len(data) == 1:
        data = mat[data[0]]
        name = f'sub-{subs["sid"]}_desc-{subs["desc"]}-{name}.tsv'
        fpath = os.path.join(path, 'coord', f'desc-{subs["desc"]}_times.json')

        convert.create_sub_struct(path, subs)
        convert.to_tsv(os.path.join(path, f'sub-{subs["sid"]}', 'ts', name), data)
        convert.to_json(fpath, data.shape, 'Time steps of the simulated time series.', 'simulations')
    else:
        print(data)


def find_mat_array(mat):
    data = []

    for k, v in mat.items():
        if type(v) not in [bytes, str, list]:
            data.append(k)

    return data
