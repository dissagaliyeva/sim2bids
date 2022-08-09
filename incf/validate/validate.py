import os
import panel as pn
from scipy.io import loadmat
import mat73
import scipy

import incf.preprocess.simulations_matlab as matlab


def validate(unique_files, all_files):
    for idx, file in enumerate(unique_files):
        if idx == 0 or idx == len(unique_files):
            continue

        name, value = file.name.replace('Specify ', ''), file.value

        if value == 'weights':
            if verify_weights(name, all_files):
                rename_weights(name, 'weights', all_files)


def verify_weights(name, all_files):
    ext = get_ext(name)

    if ext not in ['txt', 'csv', 'mat']:
        pn.state.notifications.error('Weights should be in CSV, TXT or MATLAB format. '
                                     'Please double-check your selection')
        return False

    if ext == 'mat':
        mat, cols = open_mat(get_file(all_files, name))

        if 'sc' not in [x.lower() for x in cols]:
            pn.state.notifications.error('Weights are not found in MATLAB file. Please double-check your selection')
            return False

    return True


def rename_weights(name, new_ext, all_files):
    for file in all_files:
        if file.endswith(name):
            os.rename(file, file.replace(name, new_ext))


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

    return mat, matlab.find_mat_array(mat)
