import os
import shutil
from collections import OrderedDict

import panel as pn

# define global variables
SID = None
DESC = 'default'        # short description that identifies input data
OUTPUT = '../output'    # output folder to store conversions
CENTRES = False         # whether centres.txt|nodes.txt|labels.txt were found
MULTI_INPUT = False     # whether input files include single- or multi-subjects

# define all accepted files
ACCEPTED = ['weight', 'distance', 'tract_length', 'delay', 'speed',                 # Network (net)
            'nodes', 'labels', 'centres', 'area', 'hemisphere', 'cortical',         # Coordinates (coord)
            'orientation', 'average_orientation', 'normal', 'times', 'vertices',    # Coordinates (coord)
            'faces', 'vnormal', 'fnormal', 'sensor', 'map', 'volume',               # Coordinates (coord)
            'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d',                     # Coordinates (coord)
            'vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event', 'emp'     # Timeseries (ts)
            'fc'                                                                    # Spatial (spatial)
            ]
