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
    """Two file extensions will be passed: .mat, .txt

    Parameters
    ----------
    paths :
        param output:
    test :
        return:
    paths: [str :
        
    list] :
        
    output :
         (Default value = '../../output')

    Returns
    -------

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
    """

    Parameters
    ----------
    mat_path :
        
    output :
        

    Returns
    -------

    """

    if os.stat(mat_path).st_size == 0:
        print(f'File `{mat_path}` is empty. Skipping...')
        return

    output = output.replace('/', '\\')

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
    """

    Parameters
    ----------
    txt_path :
        
    output :
        

    Returns
    -------

    """
    # Option 1: normal txt file without header
    pass


def check_filetype(files: [str, list]) -> str:
    """

    Parameters
    ----------
    files: [str :
        
    list] :
        

    Returns
    -------

    """
    # check filetype
    if isinstance(files, str):
        return get_filetype(files)

    # traverse the whole array and verify they all have the same file extension
    diff = np.unique([get_filetype(file) for file in files])

    if len(diff) == 1:
        return diff[0]
    else:
        raise TypeError(f'Files are not of the same type. Accepted files: {TSV}')


def get_filetype(file):
    """

    Parameters
    ----------
    file :
        

    Returns
    -------

    """
    return os.path.splitext(os.path.basename(file))[1]

<<<<<<< HEAD

to_tsv(['../../data/timeseries_all.mat', '../../data/ses-preop/FC.mat'])
# print(os.path.exists('../../data/timeseries_all.mat'))
=======
>>>>>>> 59d54fadb6085e3beced854cef6948636e9ba4ed
