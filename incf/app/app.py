import os
import shutil
from collections import OrderedDict

import panel as pn

# import local packages
from incf.app import utils
from incf.generate import subjects, structure


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
ACCEPTED_EXT = ['txt', 'csv', 'dat', 'h5', 'mat', 'zip', 'py']


def main(path, files, subs=None, save=False, layout=False):

    # whether to generate layout
    if layout:
        if subs is None:
            subs = subjects.Files(path, files).subs

    if save and subs is not None:
        save_output(subs, OUTPUT)

        if CODE is not None:
            save_code(subs, OUTPUT)

        # finally, remove all empty folders
        remove_empty(OUTPUT)

    if layout:
        return subs, structure.create_layout(subs, OUTPUT)
