import os
import pandas as pd
from pathlib import Path
import incf.preprocess.preprocess as prep
import incf.templates.templates as temp

import json
import sys
import csv
import scipy
import h5py
import panel as pn

sys.path.append('..')
SID = None
DURATION = 3000
TRAVERSE_FOLDERS = True
SUB_COUNT = 'Single simulation'
OUTPUT = '../output'


def check_input(path, files):
    all_files = []

    for file in files:
        fpath = os.path.join(path, file)

        if os.path.isdir(fpath) and TRAVERSE_FOLDERS:
            all_files += append_files(fpath)

    # verify there are unique files if SUB_COUNT = `single`
    if SUB_COUNT == 'Single simulation':
        if not check_compatibility(all_files):
            pn.state.notifications.error('There are multiple simulation inputs. Please select `Multiple simulations`'
                                         'option on the left.', duration=DURATION)
            return 'reset'

    pn.state.notifications.success('Processing input data...', duration=DURATION)
    return 'success'


def append_files(path, include=None):
    """
    Append all files in a specified file using recursive walk. It implements a
    top-down approach of traversing the directory.

    :param path:
    :param include:
    :return:
    """

    all_files = []
    for root, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if include is None:
                all_files.append(os.path.basename(file))
            else:
                if file in include or len(include) == 0:
                    all_files.append(os.path.join(root, file))
    return all_files


def check_compatibility(files):
    return len(set(files)) == len(files)


def check_file(path, files, save=False):
    subs = None

    if SUB_COUNT == 'Single simulation':
        subs = get_content(path, files)
    else:
        subs = get_content(path, files, single=False)

    # TODO: create layout
    # create_layout(subs)
    #
    # if save:
    #     save_output(subs, OUTPUT)


def get_content(path, files, single=True):
    all_files = []
    if single:
        for file in files:
            if os.path.isdir(os.path.join(path, file)):
                all_files += append_files(os.path.join(path, file), [])
            else:
                all_files.append(os.path.join(path, file))
    return all_files


def find_separator(path):
    """
    Find the separator/delimiter used in the file to ensure no exception
    is raised while reading files.

    :param path:
    :return:
    """
    if path.endswith('.mat') or path.endswith('.h5'):
        return

    sniffer = csv.Sniffer()

    with open(path) as fp:
        try:
            delimiter = sniffer.sniff(fp.read(5000)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(100)).delimiter
    return delimiter

# TSV = ['.mat', '.txt']
#
#
# def to_tsv(paths: [str, list], output='../output'):
#     """Two file extensions will be passed: .mat, .txt
#
#     Parameters
#     ----------
#     paths :
#         param output:
#     test :
#         return:
#     paths: [str :
#
#     list] :
#
#     output :
#          (Default value = '../../output')
#
#     Returns
#     -------
#
#     """
#
#     # create folder if not present
#     if not os.path.exists(output):
#         print(f'Creating folder `{output}`')
#         os.mkdir(output)
#
#     # convert to list
#     paths = [paths] if isinstance(paths, str) else paths
#
#     # get file types
#     file_ext = check_filetype(paths)
#     print(file_ext)
#
#     if file_ext not in TSV:
#         raise ValueError(f'Incorrect file extension: {file_ext}. Expecting to get .mat or .txt files only.')
#
#     if file_ext == TSV[0]:
#         [mat_to_tsv(path, output) for path in paths]
#     elif file_ext == TSV[1]:
#         [txt_to_tsv(path, output) for path in paths]
#
#
# def mat_to_tsv(mat_path, output):
#     """
#
#     Parameters
#     ----------
#     mat_path :
#
#     output :
#
#
#     Returns
#     -------
#
#     """
#
#     if os.stat(mat_path).st_size == 0:
#         print(f'File `{mat_path}` is empty. Skipping...')
#         return
#
#     output = output.replace('/', '\\')
#
#     mat = loadmat(mat_path)
#
#     f_name = os.path.join(output, os.path.splitext(os.path.basename(mat_path))[0])
#
#     for col in ['data', 'CON01T1_ROIts', 'CON01T1_ROIts_DK68',
#                 'FC_cc_DK68', 'FC_cc', 'ROI_ID_table']:
#         if col in mat.keys():
#             name = f'{f_name}_{col}.tsv'
#
#             pd.DataFrame(mat[col]).to_csv(os.path.join(name),
#                                           index=False, sep='\t', header=False)
#             print(f'Converted MATLAB -> TSV @ `{name}`')
#
#
# # TODO: come back to it when get enough data
# def txt_to_tsv(txt_path, output):
#     """
#
#     Parameters
#     ----------
#     txt_path :
#
#     output :
#
#
#     Returns
#     -------
#
#     """
#
#     if not os.path.exists(output):
#         os.mkdir(output)
#     file = pd.read_csv(txt_path)
#     file.to_csv(os.path.join(output, 'distances.tsv'), index=False, sep='\t', header=False)
#
#
# def check_filetype(files: [str, list]) -> str:
#     """
#
#     Parameters
#     ----------
#     files: [str :
#
#     list] :
#
#
#     Returns
#     -------
#
#     """
#     # check filetype
#     if isinstance(files, str):
#         return get_filetype(files)
#
#     # traverse the whole array and verify they all have the same file extension
#     diff = np.unique([get_filetype(file) for file in files])
#
#     if len(diff) == 1:
#         return diff[0]
#     else:
#         raise TypeError(f'Files are not of the same type. Accepted files: {TSV}')
#
#
# def get_filetype(file):
#     """
#
#     Parameters
#     ----------
#     file :
#
#
#     Returns
#     -------
#
#     """
#     return os.path.splitext(os.path.basename(file))[1]
#
#
# # to_tsv(['../../data/timeseries_all.mat', '../../data/ses-preop/FC.mat'])
# # print(os.path.exists('../../data/timeseries_all.mat'))
# # to_tsv('../../data/txt_files/weights.txt')
