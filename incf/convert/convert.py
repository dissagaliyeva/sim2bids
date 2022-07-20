import csv
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path

import pandas as pd
import panel as pn

import incf.preprocess.simulations_h5 as h5
import incf.preprocess.simulations_matlab as mat
import incf.preprocess.structure as struct
import incf.preprocess.weights_distances as wdc
import incf.templates.templates as temp
import incf.preprocess.subjects as subj
import incf.preprocess.preprocess as prep
import incf.utils as utils

sys.path.append('..')
SID = None
DURATION = 3000
TRAVERSE_FOLDERS = True

OUTPUT = '../output'
DESC = 'default'
CENTERS = False
MULTI_INPUT = False


def check_compatibility(files):
    return len(set(files)) == len(files)


# def check_input(path, files):
#     global MULTI_INPUT
#     all_files = []
#
#     for file in files:
#         fpath = os.path.join(path, file)
#
#         if os.path.isdir(fpath) and TRAVERSE_FOLDERS:
#             files = traverse_files(fpath, basename=True)
#             all_files += files
#
#     MULTI_INPUT = False if check_compatibility(all_files) else True
#     pn.state.notifications.success('Processing input data...', duration=DURATION)


def traverse_files(path: str, files=None, basename: bool = False, recursive=False) -> list:
    """
    Recursively traverse a specified folder and sub-folders. If `basename` is enabled,
    save only the file names. Otherwise, save absolute paths.

    :param recursive:
    :param files:
    :param path: str
        Path to the folder location to traverse.
    :param basename: bool
        Whether to save values by their absolute paths (False) or basename (True).
    :return: list
        Returns a list of basename or absolute paths.
    """

    if recursive:
        return recursive_walk(path, basename)

    contents = []

    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            contents += recursive_walk(path, basename)
        else:
            contents.append(file)

    return contents


def recursive_walk(path: str, basename: bool) -> list:
    contents = []

    for root, _, files in os.walk(path, topdown=True):
        for file in files:
            if basename:
                contents.append(subj.get_filename(file))
            else:
                contents.append(os.path.join(root, file))
    return contents


def check_file(path, files, subs=None, save=False):
    if subs is None:
        subs = subj.Files(path, files).subs

    if save:
        save_output(subs, OUTPUT)

    return subs, struct.create_layout(subs, OUTPUT)


def get_content(path, files, basename=False):
    if isinstance(files, str):
        return traverse_files(os.path.join(path, files), basename, recursive=True)

    all_files = []

    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            all_files += traverse_files(os.path.join(path, file), basename=basename, recursive=True)
        else:
            all_files.append(os.path.join(path, file))
    return all_files


def save_output(subs, output):
    # verify there are no conflicting folders
    conflict = len(os.listdir(output)) > 0

    def save(sub):
        for k, v in sub.items():
            if k in ['weights.txt', 'distances.txt', 'tract_lengths.txt']:
                wdc.save(sub[k], output)
            elif k in ['centres.txt']:
                wdc.save(sub[k], output, center=True)
            elif k.endswith('.mat'):
                mat.save(sub[k], output)
            elif k.endswith('.h5'):
                h5.save(sub[k], output)

    # overwrite existing content
    if conflict:
        pn.state.notifications.info('Output folder contains files. Removing them...', duration=DURATION)
        utils.rm_tree(output)
        prep.reset_index()

    # verify folders exist
    struct.check_folders(output)

    # save output files
    for k, v in subs.items():
        save(v)


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
    if file is None:
        Path(path).touch()
    else:
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
