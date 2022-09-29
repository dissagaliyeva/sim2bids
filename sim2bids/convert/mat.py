import os
import numpy as np
import pandas as pd

import panel as pn
import scipy.io as sio
import mat73
from sim2bids.app import app
from sim2bids.generate import subjects


def save_mat(sub, extract=True):
    file = traverse_file(sub['path'])
    root = os.path.dirname(sub['path'])

    if extract:
        new_files = []

        # extract files
        if file is not None:
            for k in file.keys():
                if type(file[k]) in [np.ndarray, list] and not k.startswith('__'):
                    f = file[k]

                    if len(file[k].shape) == 4:
                        f = file[k][:, 0, :, 0]

                    name = check_name(k)
                    path = os.path.join(root, name + '.txt')

                    if not os.path.exists(path):
                        new_files.append(name + '.txt')
                        pd.DataFrame(f).to_csv(path, index=None, header=None, sep='\t')

        # delete mat file
        os.remove(sub['path'])

        return new_files


def check_name(name):
    name = name.lower()
    print(name)

    if 'time' in name:
        if 'times' in name:
            return name
        return name.replace('time', 'times')
    if 'data' in name:
        return name.replace('data', 'ts')
    return name


def save_mat73(subs, folders, ses):
    return mat73.loadmat(subs['path'])


def traverse_file(path):
    name = os.path.basename(path)

    try:
        mat = sio.loadmat(path, squeeze_me=True)
    except NotImplementedError:
        return mat73.loadmat(path)
    except sio.matlab._miobase.MatReadError:
        pn.state.notifications.error(f'File `{name}` is empty! Aborting...')
        return None
    else:
        return mat