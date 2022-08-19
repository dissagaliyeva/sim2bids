import os
import json
import shutil
from collections import OrderedDict

import pandas as pd
import panel as pn

import incf.preprocess.preprocess as prep
import incf.preprocess.simulations_h5 as h5
import incf.preprocess.simulations_matlab as mat
import incf.preprocess.structure as struct
import incf.preprocess.subjects as subj
import incf.preprocess.weights_distances as wdc
import incf.preprocess.zip_traversal as z
import incf.templates.templates as temp
import incf.preprocess.coords as coords
import incf.utils as utils

SID = None
OUTPUT = '../output'
DESC = 'default'
CENTERS = False
MULTI_INPUT = False
TRAVERSE_FOLDERS = True
TO_EXTRACT = ['weights.txt', 'centres.txt', 'distances.txt',                                            # folder "net"
              'areas.txt', 'average_orientations.txt', 'cortical.txt', 'hemisphere.txt', 'normals.txt'  # folder "coord"
              ]
# ACCEPTED = {'net': ['weight', 'distance', 'tract',  'delay', 'speed'],                                # network (net)
#             'coord': ['centres', 'nodes', 'labels', 'area', 'hemisphere', 'cortical', 'orientation',  # coordinates
#                       'time', 'vertice', 'face', 'vnormal', 'fnormal', 'sensor', 'conv', 'map',       # coordinates
#                       'volume', 'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d'],                  # coordinates
#             'ts': ['vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event'],                     # ts
#             'spatial': ['fc']}                                                                        # spatial

ACCEPTED = ['weight', 'distance', 'tract',  'delay', 'speed', 'centres',
            'nodes', 'labels', 'area', 'hemisphere', 'cortical', 'orientation',
            'average_orientation', 'normal',
            'time', 'vertice', 'face', 'vnormal', 'fnormal', 'sensor', 'conv', 'map',
            'volume', 'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d',
            'vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event', 'fc']

ACCEPTED_EXT = ['txt', 'csv', 'mat', 'h5']
ALL_FILES = None


def recursive_walk(path, basename=False):
    content = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.zip') and len(set(os.listdir(root)).intersection(set(TO_EXTRACT))) < 7:
                content += z.extract_zip(os.path.join(root, file))
                continue

            file = rename_tract_lengths(file)
            if basename:
                content.append(file)
            else:
                content.append(os.path.join(root, file))

    return content


def get_content(path, files, basename=False):
    # if provided path contains only one sub-folder, and it's needed to traverse that, return the whole content
    # of the specified location.
    if isinstance(files, str):
        return recursive_walk(os.path.join(path, files))

    # otherwise, traverse all folders and get contents
    # Step 1: instantiate content holder
    contents = []

    # Step 2: traverse every selected input
    for file in files:
        # Step 3: combine path
        file_path = os.path.join(path, file)

        # Step 4: check whether the selection is a directory
        if os.path.isdir(file_path):
            # Step 4.1: traverse its content and append results
            contents += recursive_walk(file_path, basename)

        # Step 5: iterate single-files
        # Step 5.1: get the file's extension
        ext = os.path.basename(file).split('.')[-1]

        # Step 5.2: check if it's among the accepted files
        if ext in ACCEPTED_EXT:
            # Step 5.3: rename `tract_lengths` to `distances`
            contents.append(rename_tract_lengths(file_path))

    # Step 6: return contents
    return contents


def rename_tract_lengths(file):
    if 'tract_lengths' in file:
        return file.replace('tract_lengths', 'distances')
    return file


def check_file(path, files, subs=None, save=False):
    print(path, files)

    if subs is None:
        subs = subj.Files(path, files).subs

    print(subs)

    if save:
        save_output(subs, OUTPUT)

        # remove all empty folders
        remove_empty_folders(OUTPUT)

    return subs, struct.create_layout(subs, OUTPUT)


def save_output(subs, output):
    if not os.path.exists(output):
        os.mkdir(output)

    # verify there are no conflicting folders
    conflict = len(os.listdir(output)) > 0

    def save(sub, ses=None):
        for k, v in sub.items():
            folders = create_sub_struct(output, v, ses_name=ses)

            if k in ['weights.txt', 'distances.txt']:
                wdc.save(sub[k], output, folders, ses=ses)
            elif k in ['centres.txt']:
                wdc.save(sub[k], output, folders, center=True, ses=ses)
            # elif k in ['areas.txt']:
            #     wdc.save_areas(sub[k], output, ses=ses)
            elif k in TO_EXTRACT[3:]:
                coords.save_coords(sub[k], folders)
            elif k.endswith('.mat'):
                mat.save(sub[k], folders, ses=ses)
            elif k.endswith('.h5'):
                h5.save(sub[k], output, folders, ses=ses)

    # remove existing content & prepare for new data
    if conflict:
        pn.state.notifications.info('Output folder contains files. Removing them...')
        utils.rm_tree(output)
        prep.reset_index()

    # verify folders exist
    struct.check_folders(output)

    # save output files
    for k, val in subs.items():
        if 'ses-preop' in val.keys() or 'ses-postop' in val.keys():
            for k2, v in val.items():
                save(v, ses=k2)

            if os.path.exists(os.path.join(output, 'coord')):
                os.rmdir(os.path.join(output, 'coord'))

        else:
            save(val)


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


def get_shape(file, sep):
    return pd.read_csv(file, sep=sep, index_col=None, header=None).shape


def to_tsv(path, file=None, sep=None):
    if file is None:
        return
    else:
        params = {'sep': '\t', 'header': None, 'index': None}
        sep = sep if sep != '\n' else '\0'

        if isinstance(file, str) and sep is not None:
            pd.read_csv(file, index_col=None, header=None, sep=sep).to_csv(path, **params)
        else:
            try:
                pd.DataFrame(file).to_csv(path, **params)
            except ValueError:
                with open(file) as f:
                    with open(path, 'w') as f2:
                        f2.write(f.read())


def to_json(path, shape, desc, key, coords=None, **kwargs):
    inp = temp.required
    out = OrderedDict({x: '' for x in inp})

    if key != 'wd':
        struct = temp.struct[key]
        out.update({x: '' for x in struct['required']})
        out.update({x: '' for x in struct['recommend']})

    with open(path, 'w') as file:
        json.dump(temp.populate_dict(out, shape=shape, desc=desc, coords=coords, **kwargs), file)


def remove_empty_folders(path):
    """
    Recursively traverse generated output folder and remove all empty folders.
    :param path:
    :return:
    """

    # get contents of the specified path
    for root, dirs, files in os.walk(path):
        # if folder is empty, remove it
        if len(os.listdir(root)) == 0:
            os.removedirs(root)


def duplicate_folder(path):
    print('im triggered, duplicate folder')
    # create folder if it doesn't exist
    root = os.path.join('..', 'data')
    new_path = os.path.join(root, os.path.basename(os.path.dirname(path + '/')))

    if not os.path.exists(root):
        os.mkdir(root)

    if not os.path.exists(new_path):
        shutil.copytree(path, new_path, symlinks=False, ignore=None, ignore_dangling_symlinks=False,
                        dirs_exist_ok=False)
    # set PATH to a new path
    return new_path
