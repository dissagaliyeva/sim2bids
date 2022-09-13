"""
Helper functions for app.py
"""

import os
import shutil

import h5py
import numpy as np
import pandas as pd
import pylems_py2xml

from sim2bids.app import app
from sim2bids.generate import subjects as subj, zip_traversal as z


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

            # extract files from zip folder
            if file.endswith('.zip'):
                # add zip content to the files
                content += z.extract_zip(os.path.join(root, file))
                continue

            if file.endswith('.h5'):
                content += extract_h5(os.path.join(root, file))

            # if code is found, save its location
            if file.endswith('.py'):
                app.CODE = os.path.join(root, file)
                temp = pylems_py2xml.main.XML(app.CODE, save=False)

                if temp.model_name == 'hindmarshrose':
                    app.MODEL_NAME = 'SJHM3D'
                elif temp.model_name == 'oscillator':
                    app.MODEL_NAME = 'G2DOS'

            # rename tract_lengths to distances
            if 'tract_length' in files:
                file = rename_tract_lengths(file)

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
        if os.path.isdir(os.path.join(path, file)) and file.startswith('.'):
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

        # check whether the selection is a directory
        if os.path.isdir(file_path):
            # disregard folders that start with '.'
            if file_path.startswith('.'):
                shutil.rmtree(file_path)
                continue

            # if true, traverse its content and append results
            contents += recursive_walk(file_path, basename)

        # iterate over single files
        # get the file's extension
        ext = os.path.basename(file).split('.')[-1]

        if ext == 'h5':
            extract_h5(file_path)
            continue

        # check if it's among the accepted extensions
        if ext in app.ACCEPTED_EXT:
            # rename `tract_lengths` to `distances`
            contents.append(rename_tract_lengths(file_path))
        # if code is found, save its location
        elif ext == 'py':
            app.CODE = os.path.join(path, file)

    # return contents
    return contents


def rename_tract_lengths(file: str) -> str:
    return file.replace('tract_lengths', 'distances')


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


def get_model():
    files = os.listdir(os.path.join(app.OUTPUT, 'param'))

    for file in files:
        if file.startswith('model-'):
            return file.split('_')[0].split('-')[-1]
