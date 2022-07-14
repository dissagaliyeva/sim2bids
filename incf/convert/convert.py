import os
import pandas as pd
from pathlib import Path
import incf.preprocess.preprocess as prep
import incf.templates.templates as temp
import incf.preprocess.structure as struct
import incf.preprocess.weights_distances as wdc
import incf.utils as utils

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
DESC = 'default'
CENTERS = False

DEFAULT_TMPL, COORD_TMPL = 'sub-{}_desc-{}_{}.', 'desc-{}_{}.{}'


def check_compatibility(files):
    return len(set(files)) == len(files)


def check_input(path, files):
    all_files = []

    for file in files:
        fpath = os.path.join(path, file)

        if os.path.isdir(fpath) and TRAVERSE_FOLDERS:
            all_files += traverse_files(fpath, basename=True)

    # verify there are unique files if SUB_COUNT = `single`
    if SUB_COUNT == 'Single simulation':
        if not check_compatibility(all_files):
            pn.state.notifications.error('There are multiple simulation inputs. Please select `Multiple simulations`'
                                         'option on the left.', duration=DURATION)
            return 'reset'

    pn.state.notifications.success('Processing input data...', duration=DURATION)
    return 'success'


def traverse_files(path: str, basename: bool = False) -> list:
    """
    Recursively traverse a specified folder and sub-folders. If `basename` is enabled,
    save only the file names. Otherwise, save absolute paths.

    :param path: str
        Path to the folder location to traverse.
    :param basename: bool
        Whether to save values by their absolute paths (False) or basename (True).
    :return: list
        Returns a list of basename or absolute paths.
    """

    contents = []

    for root, _, files in os.walk(path, topdown=True):
        for file in files:
            if basename:
                contents.append(get_filename(file))
            else:
                contents.append(os.path.join(root, file))

    return contents


def check_file(path, files, save=False):
    if SUB_COUNT == 'Single simulation':
        subs = prepare_subs(get_content(path, files))
    else:
        subs = get_content(path, files, single=False)

    if save:
        save_output(subs, OUTPUT)

    # return struct.create_layout(subs, OUTPUT)
    out = struct.create_layout(subs, OUTPUT)
    print('out:', out)
    return out


def get_content(path, files, single=True):
    global CENTERS

    all_files = []
    if single:
        for file in files:
            if file == 'centres.txt':
                CENTERS = True

            if os.path.isdir(os.path.join(path, file)):
                all_files += traverse_files(os.path.join(path, file))
            else:
                all_files.append(os.path.join(path, file))
        return all_files


def prepare_subs(file_paths):
    subs = {}
    for file_path in file_paths:
        name = get_filename(file_path)
        subs[name] = {
            'fname': name,
            'sid': SID,
            'sep': find_separator(file_path),
            'desc': DESC,
            'path': file_path,
            'ext': get_file_ext(file_path),
            'name': name.split('.')[0]
        }

        if subs[name]['name'] in ['tract_lengths', 'tract_length']:
            subs[name]['name'] = 'distances'
    return subs


def get_filename(path):
    return os.path.basename(path)


def get_file_ext(path):
    return path.split('.')[-1]


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

    delimiter = '\s' if delimiter == ' ' else delimiter
    return delimiter


def save_output(subs, output):
    # verify there are no conflicting folders
    conflict = len(os.listdir(output)) > 0

    def save():
        for k, v in subs.items():
            if k in ['weights.txt', 'distances.txt']:
                wdc.save(subs[k], output)
            elif k in ['centres.txt']:
                wdc.save(subs[k], output, center=True)
            elif k.endswith('.mat'):
                pass
            elif k.endswith('.h5'):
                pass

    if SUB_COUNT == 'Single simulation':
        # overwrite existing content
        if conflict:
            pn.state.notifications.info('Output folder contains files. Removing them...', duration=DURATION)
            utils.rm_tree(output)

        # verify folders exist
        struct.check_folders(output)

        # save output files
        save()


def create_sub_struct(path, subs):
    sub = os.path.join(path, f"sub-{subs['sid']}")
    net = os.path.join(sub, 'net')
    spatial = os.path.join(sub, 'spatial')
    ts = os.path.join(sub, 'ts')

    for folder in [sub, net, spatial, ts]:
        if not os.path.exists(folder):
            print(f'Creating folder `{folder}`')
            os.mkdir(folder)

    return sub, net, spatial, ts


def get_shape(file, sep):
    return pd.read_csv(file, sep=sep, index_col=None, header=None).shape


def to_tsv(path, file=None):
    params = {'sep': '\t', 'header': None, 'index': None}
    pd.DataFrame(file).to_csv(path, **params)


def to_json(path, shape, desc, ftype, coords=None):
    json_file = None

    if ftype == 'simulations':
        json_file = temp.merge_dicts(temp.JSON_template, temp.JSON_simulations)
    elif ftype == 'centers':
        json_file = temp.JSON_centers
    elif ftype == 'wd':
        json_file = temp.JSON_template

    if json_file is not None:
        with open(path, 'w') as f:
            json.dump(temp.populate_dict(json_file, shape=shape, desc=desc, coords=coords), f)



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
