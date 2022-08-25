import os
import shutil
from collections import OrderedDict

import panel as pn

# import local packages
import incf.utils
from incf.app import utils
from incf.generate import subjects, structure
from incf.preprocess import preprocess as prep
from incf.convert import save as conv


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


def main(path: str, files: list, subs: dict = None, save: bool = False, layout: bool = False):
    """
    Main brain function that creates subjects, auto-generated structure,
    and saves converted files.

    :param path:
    :param files:
    :param subs:
    :param save:
    :param layout:
    :return:
    """
    # whether to generate layout
    if layout:
        # if no subjects are passed, define them
        if subs is None:
            subs = subjects.Files(path, files).subs

    # only save conversions if 'save' is True
    if save and subs is not None:
        # save conversions
        save_output(subs)

        # save code
        if CODE is not None:
            save_code(subs)

        # finally, remove all empty folders
        remove_empty()

    # return subjects and possible layouts only if it's enabled
    if layout:
        return subs, structure.create_layout(subs)

    # otherwise, return None
    return


def save_output(subs):
    """

    :param subs:
    :return:
    """
    # prepare the output folder
    check_output_folder()

    def save(sub, ses=None):
        for k, v in sub.items():
            # create folders according to session and subject count types
            folders = create_sub_struct(OUTPUT, v, ses_name=ses)

            if 'weight' in k or 'distance' in k:
                conv.save(sub[k], folders, ses=ses, name='wd')


    # iterate over files and save them
    for k, v in subs.items():
        if 'ses-preop' in v.keys() or 'ses-postop' in v.keys():
            for k2, v2 in v.items():
                save(v2, ses=k2)



def check_output_folder():
    # check if the output folder already contains files,
    # if true, notify about removal and remove folder with its contents
    conflict = len(os.listdir(OUTPUT)) > 0

    if conflict:
        pn.state.notifications.info('Output folder contains files. Removing them...')
        incf.utils.rm_tree(OUTPUT)
        prep.reset_index()

    # create the folder that will store conversions
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)

    # verify folders exist
    structure.check_folders(OUTPUT)


def create_sub_struct(path, subs, ses_name=None):
    if ses_name in ['ses-preop', 'ses-postop']:
        sub = os.path.join(path, subs['sid'])
        ses = os.path.join(sub, ses_name)
        net_ses = os.path.join(ses, 'net')
        spatial_ses = os.path.join(ses, 'spatial')
        coord_ses = os.path.join(ses, 'coord')
        ts_ses = os.path.join(ses, 'ts')
        folders = [sub, ses, net_ses, spatial_ses, coord_ses, ts_ses]
    else:
        sub = os.path.join(path, subs['sid'])
        net = os.path.join(sub, 'net')
        spatial = os.path.join(sub, 'spatial')
        ts = os.path.join(sub, 'ts')

        if MULTI_INPUT:
            coord = os.path.join(sub, 'coord')
            folders = [sub, net, spatial, coord, ts]
        else:
            folders = [sub, net, spatial, ts]

    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)

    return folders
