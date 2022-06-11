import os
import re
import glob
import json
import logging
from scipy.io import loadmat

import numpy as np
import pandas as pd


TSV = ['.mat', '.txt']


def to_tsv(val, output='../output'):
    """
    Two file extensions will be passed: .mat, .txt
    :param val:
    :param output:
    :return:
    """

    # create folder if not present
    if not os.path.exists(output):
        print(f'Creating folder `{output}`')
        os.mkdir(output)

    file_ext = check_filetype(val)

    if file_ext not in TSV:
        raise ValueError(f'Incorrect file extension: {file_ext}. Expecting to get .mat, .txt only.')

    # verify the path exists
    assert os.path.exists(val), f'`{val}` does not exist.'


def mat_to_tsv(mat_path, output):
    mat = loadmat(mat_path)
    f_name = os.path.join(output, os.path.splitext(os.path.basename(mat_path))[0])
    pd.DataFrame(mat['data']).to_csv(os.path.join(output, f_name),
                                     index=False, sep='\t', header=False)
    print(f'Converted MATLAB -> TSV @{f_name}')


def txt_to_tsv(txt_path, output):
    # Option 1: normal txt file without header
    pd.read_csv(txt_path)


def check_filetype(files: [str, list]) -> str:

    # check whether it's a directory
    if os.path.isdir(files):
        print('it is a folder')
        # TODO: add functionality for directory traversal

    # check filetype
    if isinstance(files, str):
        return get_filetype(files)

    # traverse the whole array and verify they all have the same file extension
    diff = set([get_filetype(file) for file in files])

    if len(diff) == 1 and diff in ['.mat', '.txt']:
        return str(diff)

    raise TypeError('Files are not the same type or of different type. Accepted types: .mat, .txt')


def get_filetype(file):
    return os.path.splitext(os.path.basename(file))[1]


# to_tsv(look.mats)
print(to_tsv('../data/dcm'))


