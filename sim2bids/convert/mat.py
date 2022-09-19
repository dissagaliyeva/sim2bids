import os
import pandas as pd

import panel as pn
import scipy.io as sio
import mat73
from sim2bids.app import app
from sim2bids.generate import subjects


def save_mat(sub, folders, ses=None):
    file = traverse_file(sub['path'])
    root = os.path.dirname(sub['path'])

    # extract files
    if file is not None:
        for k in file.keys():
            if subjects.accepted(k):
                # save files separately
                print(file[k])
                pd.DataFrame(file[k]).to_csv(os.path.join(root, k + '.txt'),
                                             index=None, header=None, sep='\t')


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