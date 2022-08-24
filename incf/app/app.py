import os
import shutil
from collections import OrderedDict

import panel as pn

# import local packages
from incf.app import utils
from incf.generate import zip_traversal as z


# define global variables
SID = None
DESC = 'default'        # short description that identifies input data
OUTPUT = '../output'    # output folder to store conversions
CENTRES = False         # whether centres.txt|nodes.txt|labels.txt were found
MULTI_INPUT = False     # whether input files include single- or multi-subjects
ALL_FILES = None        # list of all file paths (gets supplemented in subjects.py)
CODE = None             # path to python code if exists

# define all accepted files
ACCEPTED = ['weight', 'distance', 'tract_length', 'delay', 'speed',                 # Network (net)
            'nodes', 'labels', 'centres', 'area', 'hemisphere', 'cortical',         # Coordinates (coord)
            'orientation', 'average_orientation', 'normal', 'times', 'vertices',    # Coordinates (coord)
            'faces', 'vnormal', 'fnormal', 'sensor', 'map', 'volume',               # Coordinates (coord)
            'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d',                     # Coordinates (coord)
            'vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event', 'emp'     # Timeseries (ts)
            'fc']                                                                   # Spatial (spatial)

# define accepted extensions
ACCEPTED_EXTS = ['txt', 'csv', 'dat', 'h5', 'mat', 'zip', 'py']


def recursive_walk(path: str, basename: bool = False) -> list:
    """
    Recursively collect file paths using os.walk. If `basename` is True,
    get only file names. Otherwise, get all absolute paths.

    :param path:
        Path to a folder
    :param basename:
        Whether to store file names only.
    :return:
        List of either absolute paths or file names.
    """

    global CODE

    # create empty list to store paths
    content = []

    # recursively walk the directory
    for root, _, files in os.walk(path):
        for file in files:
            # extract files
            if file.endswith('.zip'):
                content += z.extract_zip(os.path.join(root, file))

                # remove zip folder
                os.remove(file)
                continue
            if file.endswith('.py'):
                CODE = os.path.join(root, file)

            file = utils.rename_tract_lengths(file)
            if basename:
                content.append(file)
            else:
                content.append(os.path.join(root, file))

    return content
