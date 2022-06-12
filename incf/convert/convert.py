import os
import re
import glob
import json
import logging
import shutil
from scipy.io import loadmat

import numpy as np
import pandas as pd

TSV = ['.mat', '.txt']


def to_tsv(paths: [str, list], output='../../output'):
    """
    Two file extensions will be passed: .mat, .txt
    :param paths:
    :param output:
    :param test:
    :return:
    """

    # create folder if not present
    if not os.path.exists(output):
        print(f'Creating folder `{output}`')
        os.mkdir(output)

    # convert to list
    paths = [paths] if isinstance(paths, str) else paths

    # get file types
    file_ext = check_filetype(paths)

    if file_ext not in TSV:
        raise ValueError(f'Incorrect file extension: {file_ext}. Expecting to get .mat or .txt files only.')

    if file_ext == TSV[0]:
        [mat_to_tsv(path, output) for path in paths]
    elif file_ext == TSV[1]:
        [txt_to_tsv(path, output) for path in paths]


def mat_to_tsv(mat_path, output):
    output = output.replace('/', '\\')

    if os.stat(mat_path).st_size == 0:
        print(f'File `{mat_path}` is empty. Skipping...')
        return None

    mat = loadmat(mat_path)

    f_name = os.path.join(output, os.path.splitext(os.path.basename(mat_path))[0])

    for col in ['data', 'CON01T1_ROIts', 'CON01T1_ROIts_DK68',
                'FC_cc_DK68', 'FC_cc', 'ROI_ID_table']:
        if col in mat.keys():
            name = f'{f_name}_{col}.tsv'

            pd.DataFrame(mat[col]).to_csv(os.path.join(name),
                                          index=False, sep='\t', header=False)
            print(f'Converted MATLAB -> TSV @ `{name}`')


# TODO: come back to it when get enough data
def txt_to_tsv(txt_path, output):
    # Option 1: normal txt file without header
    pass


def check_filetype(files: [str, list]) -> str:
    # check filetype
    if isinstance(files, str):
        return get_filetype(files)

    # traverse the whole array and verify they all have the same file extension
    diff = np.unique([get_filetype(file) for file in files])

    if len(diff) == 1 and diff in TSV:
        return diff[0]
    else:
        raise TypeError('Files are not the same type or of different type. Accepted types: .mat, .txt')


def get_filetype(file):
    return os.path.splitext(os.path.basename(file))[1]


to_tsv('../../data/ses-preop/HRF.mat')
