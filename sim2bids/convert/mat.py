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


def save_mat(sub, og_path, extract=True):
    file = traverse_file(sub['path'])
    root = os.path.dirname(sub['path'])
    multi_folder = False

    if og_path == root:
        multi_folder = True

    if extract:
        new_files = []

        # extract files
        if file is not None:
            for k in file.keys():
                if type(file[k]) in [np.ndarray, list] and not k.startswith('__'):
                    f = file[k]

                    if len(file[k].shape) == 4:
                        f = file[k][:, 0, :, 0]

                    if len(file[k].shape) == 3:
                        f = file[k][:, 0, :]

                    name = check_name(k)
                    minutes = re.findall(r'[0-9]+min', sub['path'])
                    name = f'{name}_{minutes[0]}' if len(minutes) > 0 else name

                    if multi_folder:
                        sid, folder = sub['sid'], os.path.join(root, sub['sid'])

                        if not os.path.exists(folder):
                            os.mkdir(folder)

                        # find matches for unique patients and transfer files there,
                        # e.g., weights and distances
                        match = subjects.find_matches([sub['path']])

                        print('match:', match)

                        if len(match) > 0:
                            for file in os.listdir(og_path):
                                print('all files one-by-one:', file)

                                if match[0] in file:
                                    shutil.move(os.path.join(og_path, file), os.path.join(og_path, sid))

                        path = os.path.join(folder, name + '.txt')
                    else:
                        path = os.path.join(root, name + '.txt')

                    if not os.path.exists(path):
                        new_files.append(name + '.txt')
                        pd.DataFrame(f).to_csv(path, index=None, header=None, sep='\t')

        # delete mat file
        os.remove(sub['path'])

        return new_files


def check_name(name):
    name = name.lower()

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