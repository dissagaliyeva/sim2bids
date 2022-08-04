import glob
import json
import os
import sys
import zipfile
from pathlib import Path

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
import incf.utils as utils

SID = None
OUTPUT = '../output'
DESC = 'default'
DURATION = 3000
CENTERS = False
MULTI_INPUT = False
TRAVERSE_FOLDERS = True
TO_EXTRACT = ['weights.txt', 'centres.txt', 'distances.txt', 'average_orientations.txt',
              'areas.txt', 'cortical.txt', 'hemisphere.txt']
ACCEPTED_EXT = ['txt', 'csv', 'mat', 'h5']


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
            file = rename_tract_lengths(file)
            contents.append(file)

    # Step 6: return contents
    return contents


def rename_tract_lengths(file):
    if 'tract_lengths' in file:
        return file.replace('tract_lengths', 'distances')
    return file


def check_file(path, files, subs=None, save=False):
    if subs is None:
        subs = subj.Files(path, files).subs

    print(subs)
    if save:
        save_output(subs, OUTPUT)

        # remove zip folder contents
        # if isinstance(ZIP_CONTENT, list):
        #     print('zipfiles:', ZIP_CONTENT)
        #     print('contents:', get_content(path, files))
        #
        #     for content in get_content(path, files):
        #         print('content:', content)
        #         file = content.split('\\')[-1].split('.')[0]
        #         file = file.replace('_preop', '') if 'preop' in file else file.replace('_postop', '') if 'postop' in file else file
        #         print('file:', file)
        #
        #         if file in ZIP_CONTENT:
        #             os.remove(content)
        #
        #         ZIP_CONTENT = None

    return subs, struct.create_layout(subs, OUTPUT)


def save_output(subs, output):
    if not os.path.exists(output):
        os.mkdir(output)

    # verify there are no conflicting folders
    conflict = len(os.listdir(output)) > 0

    def save(sub, ses=None):
        for k, v in sub.items():
            print(k, v, end='\n\n')
            if k in ['weights.txt', 'distances.txt', 'tract_lengths.txt']:
                wdc.save(sub[k], output, ses=ses)
            elif k in ['centres.txt']:
                wdc.save(sub[k], output, center=True, ses=ses)
            # elif k in TO_EXTRACT[3:]:

            elif k.endswith('.mat'):
                mat.save(sub[k], output, ses=None)
            elif k.endswith('.h5'):
                h5.save(sub[k], output, ses=None)

    # overwrite existing content
    if conflict:
        pn.state.notifications.info('Output folder contains files. Removing them...', duration=DURATION)
        utils.rm_tree(output)
        prep.reset_index()

    # verify folders exist
    struct.check_folders(output)

    # save output files
    for k, val in subs.items():
        if 'ses-preop' in val.keys():
            # create_sub_struct(output, subs, ses=True)
            for k2, v in val.items():
                save(v, ses=k2)
        else:
            save(val)


def create_sub_struct(path, subs, ses=None):
    if ses is None:
        sub = os.path.join(path, f"sub-{subs['sid']}")
        net = os.path.join(sub, 'net')
        spatial = os.path.join(sub, 'spatial')
        ts = os.path.join(sub, 'ts')
        folders = [sub, net, spatial, ts]
    else:
        sub = os.path.join(path, f"sub-{subs['sid']}")
        preop = os.path.join(sub, 'ses-preop')
        postop = os.path.join(sub, 'ses-postop')
        net_preop = os.path.join(preop, 'net')
        spatial_preop = os.path.join(preop, 'spatial')
        coord_preop = os.path.join(preop, 'coord')
        ts_preop = os.path.join(preop, 'ts')
        net_postop = os.path.join(postop, 'net')
        spatial_postop = os.path.join(postop, 'spatial')
        coord_postop = os.path.join(postop, 'coord')
        ts_postop = os.path.join(postop, 'ts')

        folders = [sub, preop, postop, net_preop, spatial_preop, coord_preop,
                   ts_preop, net_postop, spatial_postop, coord_postop, ts_postop]

    for folder in folders:
        if not os.path.exists(folder):
            print(f'Creating folder `{folder}`')
            os.mkdir(folder)

    return folders


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
