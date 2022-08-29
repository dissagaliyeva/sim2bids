"""
Helper functions for app.py
"""

import os

from incf.app import app
from incf.generate import zip_traversal as z


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
            # extract files from zip folder
            if file.endswith('.zip'):
                # add zip content to the files
                content += z.extract_zip(os.path.join(root, file))

                continue

            # if code is found, save its location
            if file.endswith('.py'):
                app.CODE = os.path.join(root, file)

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

    # otherwise, traverse all folders and get contents
    # create empty list to store paths
    contents = []

    # traverse files
    for file in files:
        # combine path
        file_path = os.path.join(path, file)

        # check whether the selection is a directory
        if os.path.isdir(file_path):
            # if true, traverse its content and append results
            contents += recursive_walk(file_path, basename)

        # iterate over single files
        # get the file's extension
        ext = os.path.basename(file).split('.')[-1]

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
        'ts': ['ts', 'emp', 'vars', 'stimuli', 'noise', 'spikes', 'raster', 'events'],
        'spatial': ['fc']
    }
