import os
import re
import shutil

import numpy as np
import pandas as pd

import panel as pn
import scipy.io as sio
import mat73
from sim2bids.app import app
from sim2bids.generate import subjects


def save_mat(sub, og_path, extract=False):
    file = traverse_file(sub['path'])
    root = os.path.dirname(sub['path'])
    multi_folder, extracted = og_path == root, False

    if extract:
        new_files = []

        # extract files
        if file is not None:
            # first, check if there are matches according to unique ID
            # find matches for unique patients and transfer files there,
            # e.g., weights and distances
            # transfer_files(sub, og_path)

            # iterate over matlab files and extract files
            for k in file.keys():
                if not k.startswith('__') and type(file[k]) in [np.ndarray, list]:
                    f = file[k]

                    if len(file[k].shape) == 4:
                        f = file[k][:, 0, :, 0]

                    if len(file[k].shape) == 3:
                        f = file[k][:, 0, :]

                    name = check_name(os.path.join(root, k))
                    minutes = re.findall(r'[0-9]+min', sub['path'])
                    name = f'{name}_{minutes[0]}' if len(minutes) > 0 else name

                    if multi_folder:

                        path = os.path.join(os.path.join(root, sub['sid']), name + '.txt')
                    else:
                        path = os.path.join(root, name + '.txt')

                    if not os.path.exists(path):
                        extracted = True
                        new_files.append(name + '.txt')
                        pd.DataFrame(f).to_csv(path, index=None, header=None, sep='\t')

            if extracted:
                # delete mat file
                os.remove(sub['path'])

        return new_files


def transfer_files(sub, og_path):
    """
    Iterate over folder and find unique ID's corresponding files
    """
    root = os.path.dirname(sub['path'])

    match = subjects.find_matches([sub['path']])
    sid, folder = sub['sid'], os.path.join(root, sub['sid'])

    if len(match) > 0:
        if not os.path.exists(folder):
            os.mkdir(folder)

        for f in os.listdir(og_path):
            if os.path.isdir(os.path.join(og_path, f)) or f.endswith('mat'):
                continue
            if match[0] in f:
                basename = f.replace(match[0], '').strip('_')
                shutil.move(os.path.join(og_path, f), os.path.join(og_path, sub['sid'], basename))


def check_name(name):
    name = subjects.get_name(name).lower()

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
    except FileNotFoundError:
        return None
    else:
        return mat
