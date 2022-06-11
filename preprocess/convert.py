import os
import re
import glob
import json
import logging
from scipy.io import loadmat

import numpy as np
import pandas as pd


TSV = ['.mat', '.txt']


def to_tsv(paths: [str, list], output='../output'):
    """
    Two file extensions will be passed: .mat, .txt
    :param path:
    :param output:
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

    # verify the path exists
    assert os.path.exists(paths), f'`{paths}` does not exist.'

    if file_ext == TSV[0]:
        [mat_to_tsv(path, output) for path in paths]
    elif file_ext == TSV[1]:
        [txt_to_tsv(path, output) for path in paths]


def mat_to_tsv(mat_path, output):
    mat = loadmat(mat_path)
    f_name = os.path.join(output, os.path.splitext(os.path.basename(mat_path))[0])
    pd.DataFrame(mat['data']).to_csv(os.path.join(output, f_name),
                                     index=False, sep='\t', header=False)
    print(f'Converted MATLAB -> TSV @{f_name}')


# TODO: come back to it when get enough data
def txt_to_tsv(txt_path, output):
    # Option 1: normal txt file without header
    pass


def check_filetype(files: [str, list]) -> str:
    # check whether it's a directory
    # if os.path.isdir(files):
    #     print(f'Got a folder {files} instead of file(s). Traversing the content...')
    #     # TODO: add functionality for directory traversal

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


