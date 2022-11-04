"""
Helper functions for app.py
"""

import os
import re
import shutil

import h5py
import numpy as np
import pandas as pd
import pylems_py2xml

from sim2bids.app import app
from sim2bids.generate import subjects as subj, zip_traversal as z
from sim2bids.convert import mat
from sim2bids.preprocess import preprocess
from sim2bids.generate import utils as gen_utils


ACCEPTED_RHYTHMS = ['alpha', 'delta', 'theta', 'gamma', 'beta']
RHYTHMS = dict()


def recursive_walk(path: str, basename: bool = False) -> list:
    """
    Recursively collect file paths using os.walk. If `basename` is True,
    get only file names. Otherwise, get all absolute paths.

    Parameters
    ----------
    path : str
        Path to a folder
    basename : bool
        Whether to store file names only. (Default value = False)

    Returns
    -------
    """
    # create empty list to store paths
    content = []

    # recursively walk the directory
    for root, _, files in os.walk(path):
        for file in files:
            # ignore checkpoints
            if '.ipynb_checkpoints' in file:
                continue

            # find rhythms
            find_rhythm(os.path.join(root, file))

            # extract files from zip folder
            if file.endswith('.zip'):
                # add zip content to the files
                content += z.extract_zip(os.path.join(root, file))

                # remove zip folder to not get into recursion
                os.remove(os.path.join(root, file))
                continue

            if file.endswith('.h5'):
                content += extract_h5(os.path.join(root, file))

            if file.endswith('.mat'):
                content += extract_mat(os.path.join(root, file), path)

            if 'times' in file:
                app.TIMES.append(subj.accepted(file)[-1])
                app.TIMES = list(set(app.TIMES))

            # if code is found, save its location
            if file.endswith('.py'):
                app.CODE = os.path.join(root, file)
                temp = pylems_py2xml.main.XML(app.CODE, save=False)

                if temp.model_name == 'hindmarshrose':
                    app.MODEL_NAME = 'SJHM3D'
                elif temp.model_name == 'oscillator':
                    app.MODEL_NAME = 'G2DOS'

            # rename tract_lengths to distances

            # save file name
            if basename:
                content.append(file)

            # save absolute path
            else:
                content.append(os.path.join(root, file))

    # return contents
    return content


def get_content(path: str, files: [str, list], basename: bool = False) -> list:
    """

    Parameters
    ----------
    path :
        param files:
    basename :
        return:
    path: str :

    files: [str :

    list] :

    basename: bool :
         (Default value = False)

    Returns
    -------

    """
    # if provided path contains only one sub-folder, and it's needed to traverse that,
    # return the whole content of the specified location.
    if isinstance(files, str):
        return recursive_walk(os.path.join(path, files))

    for file in files:
        if os.path.isdir(os.path.join(path, file)) and (file.startswith('.ipy') or file.startswith('.git') or
                                                        file.startswith('.MS') or file.startswith('.idea') or
                                                        file.startswith('vscode')):
            shutil.rmtree(os.path.join(path, file))

    # preprocess folder and remove all folders/files starting with '.'
    # files = preprocess_folders(files, path)

    # otherwise, traverse all folders and get contents
    # create empty list to store paths
    contents = []

    # traverse files
    for file in files:
        if '.ipynb_checkpoints' in file:
            continue

        # combine path
        file_path = os.path.join(path, file)

        if file.endswith('.m') or file.endswith('.R'):
            if app.CODE is None:
                app.CODE = []
            app.CODE.append(file_path)
            continue

        find_rhythm(file_path)

        if 'CHANGES' in file or 'participants' in file or 'README' in file:
            app.MISSING.append(file_path)

        # # check whether the selection is a directory
        if os.path.isdir(file_path):
            # if true, traverse its content and append results
            contents += recursive_walk(file_path, basename)

        # iterate over single files
        # get the file's extension
        ext = os.path.basename(file).split('.')[-1]

        if ext == 'h5':
            extract_h5(file_path)
            continue

        if file.endswith('.mat'):
            contents += extract_mat(os.path.join(path, file), path)
            continue

        # check if it's among the accepted extensions
        if ext in app.ACCEPTED_EXT:
            file = file_path

            if basename:
                # rename `tract_lengths` to `distances`
                contents.append(os.path.basename(file))
            else:
                contents.append(file)

        # if code is found, save its location
        elif ext == 'py':
            app.CODE = os.path.join(path, file)

    # return contents
    return contents


def find_rhythm(path):
    for rhythm in ACCEPTED_RHYTHMS:
        if rhythm in path:
            minutes = re.findall(r'[0-9]+min', path)
            if minutes:
                RHYTHMS[rhythm + '_' + minutes[0]] = []
                return
            RHYTHMS[rhythm] = []


# def rename_tract_lengths(file: str) -> str:
#     return file.replace('tract_lengths', 'distances')


def get_files():
    return {
        'net': ['weights', 'distances', 'delays', 'speed'],
        'coord': ['times', 'centres', 'orientations', 'areas', 'hemispheres',
                  'cortical', 'nodes', 'labels', 'vertices', 'faces', 'vnormals',
                  'fnormals', 'sensors', 'app', 'map', 'volumes',
                  'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d'],
        'ts': ['ts', 'emp', 'vars', 'stimuli', 'noise', 'spikes', 'raster', 'events', 'bold'],
        'spatial': ['fc']
    }


def extract_h5(path) -> list:
    contents = []

    file = h5py.File(path)

    # check if the h5 file contains weights, distances, areas, cortical, and hemisphere
    if 'datatypes' in path:
        for f in file.keys():
            if f in ['region_labels', 'distances']: continue

            content, name = file[f][:], f

            if f == 'centres':
                content = np.column_stack([file['region_labels'][:].astype(str), file['centres'][:]])

            if f == 'tract_lengths':
                name = 'distances'

            new_path = os.path.join(os.path.dirname(path), f'{name}.txt')
            pd.DataFrame(content, index=None).to_csv(new_path, header=None, index=None, sep='\t')
            contents.append(new_path)
    else:
        name = subj.get_filename(path)
        model = name.split('_')[0].lower()

        if model in ['generic2doscillator', 'hindmarshrose']:
            app.H5_CONTENT['model'] = model

        if len(list(file.keys())) > 0:
            for k in file.keys():
                if k not in app.H5_CONTENT.keys():
                    app.H5_CONTENT[k] = [file[k][:][0]]

    return contents


def extract_mat(path, og_path) -> list:
    return mat.save_mat({'path': path, 'sid': preprocess.create_uuid(numbers=True)}, og_path, extract=True)


def get_model():
    files = os.listdir(os.path.join(app.OUTPUT, 'param'))

    for file in files:
        if file.startswith('model-'):
            return file.split('_')[0].split('-')[-1]


def infer_model():
    if isinstance(app.CODE, str):
        content = gen_utils.open_file(app.CODE)
        model = re.findall(r'(?:hindmarsh|wongwang|oscillator)', ''.join(content), flags=re.IGNORECASE)

        if model:
            model = model[0].lower()
            if 'hindmarsh' in model:
                app.MODEL_NAME = 'HindmarshRose'
            elif 'wongwang' in model:
                app.MODEL_NAME = 'ReducedWongWang'
            elif 'oscillator' in model:
                app.MODEL_NAME = 'Generic2dOscillator'
