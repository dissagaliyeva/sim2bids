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
CENTERS = False
MULTI_INPUT = False
TRAVERSE_FOLDERS = True
TO_EXTRACT = ['tract_lengths.txt', 'weights.txt', 'centres.txt']
ACCEPTED_EXT = ['txt', 'csv', 'mat', 'h5']
EXCLUDE = ['areas.txt', 'average_orientations.txt', 'cortical.txt', 'hemisphere.txt']
SES_FILES = ['tract_lengths_preop.txt', 'weights_preop.txt', 'centres_preop.txt',
              'tract_lengths_postop.txt', 'weights_postop.txt', 'centres_postop.txt',
              'distances.txt', 'distances_preop.txt', 'distances_postop.txt']


def recursive_walk(path, basename=False):
    content = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.zip') and len(set(os.listdir(root)).intersection(set(SES_FILES))) == 0:
                content += z.extract_zip(os.path.join(root, file))
                continue

            file = rename_tract_lengths(file)
            if file not in EXCLUDE:
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

            # Step 5.4: check if the file ends with txt, and it's not among the files that cannot be used
            if (ext == 'txt' and file not in EXCLUDE) or ext != 'txt':
                # Step 5.5: append file
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

    if save:
        pass
        # save_output(subs, OUTPUT)
        #
        # # remove zip folder contents
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


# print(get_content('C:\\Users\\dinar\\Desktop\\gsoc_data', ['brain_tumor']))







#
# sys.path.append('..')
# SID = None
# DURATION = 3000
# TRAVERSE_FOLDERS = True
# import zipfile
#
# OUTPUT = '../output'
# DESC = 'default'
# CENTERS = False
# MULTI_INPUT = False
# ZIP_CONTENT = None
#
#
# def check_compatibility(files):
#     return len(set(files)) == len(files)
#
#
# def traverse_files(path: str, files=None, basename: bool = False, recursive=False) -> list:
#     """
#     Recursively traverse a specified folder and sub-folders. If `basename` is enabled,
#     save only the file names. Otherwise, save absolute paths.
#     :param recursive:
#     :param files:
#     :param path: str
#         Path to the folder location to traverse.
#     :param basename: bool
#         Whether to save values by their absolute paths (False) or basename (True).
#     :return: list
#         Returns a list of basename or absolute paths.
#     """
#
#     if recursive:
#         return recursive_walk(path, basename)
#
#     contents = []
#
#     for file in files:
#         if os.path.isdir(os.path.join(path, file)):
#             contents += recursive_walk(path, basename)
#         else:
#             contents.append(file)
#
#     return contents
#
#
# def recursive_walk(path: str, basename: bool) -> list:
#     global ZIP_CONTENT
#
#     contents, zip_idx = [], None
#     to_extract = ['tract_lengths.txt', 'weights.txt', 'centres.txt',
#                   'tract_lengths_preop.txt', 'weights_preop.txt', 'centres_preop.txt',
#                   'tract_lengths_postop.txt', 'weights_postop.txt', 'centres_postop.txt',
#                   'distances.txt', 'distances_preop.txt', 'distances_postop.txt']
#
#     # present =
#     # zip_present = False
#
#     for root, _, files in os.walk(path, topdown=True):
#         exists = False
#         for file in files:
#             if file in to_extract:
#                 exists = True
#
#             if not file.endswith('.zip'):
#                 if basename:
#                     contents.append(subj.get_filename(file))
#                 else:
#                     contents.append(os.path.join(root, file))
#             else:
#                 if file.endswith('.zip'):
#                     print(file)
#                     if not exists:
#                         if ZIP_CONTENT is None:
#                             ZIP_CONTENT = get_zip_content(os.path.join(root, file))
#                         extract_files(os.path.join(root, file))
#                         contents += glob.glob(os.path.join(root, '*txt'))
#
#     return contents
#
#
# def get_zip_content(path):
#     # specifying the zip file name
#     file_name = path
#
#     # opening the zip file in READ mode
#     with zipfile.ZipFile(file_name, 'r') as file:
#         return [x for x in file.namelist() if x != '.DS_Store']
#
#
# def extract_files(path):
#     basename = subj.get_filename(path)
#     parent = path.replace(basename, '')
#     suffix = os.path.dirname(path).split('\\')[-1].split('-')[-1]
#
#     to_extract = ['tract_lengths.txt', 'weights.txt', 'centres.txt']
#     archive = zipfile.ZipFile(path)
#
#     for ext in to_extract:
#         archive.extract(ext, path=parent)
#         os.rename(os.path.join(parent, ext),
#                   os.path.join(parent, ext.replace('.', f'_{suffix}.')))
#
#
# def verify_zip_files(paths):
#     for path in paths:
#         basename = subj.get_filename(path)
#         suffix = os.path.dirname(path).split('\\')[-1].split('-')[-1]
#
#         if basename.startswith('centres') and basename != f'centres_{suffix}.txt':
#             os.rename(path, path.replace(basename, f'centres_{suffix}.txt'))
#         elif basename.startswith('weights') and basename != f'weights_{suffix}.txt':
#             os.rename(path, path.replace(basename, f'weights_{suffix}.txt'))
#         elif basename.startswith('tract_lengths') and basename != f'tract_lengths_{suffix}.txt':
#             os.rename(path, path.replace(basename, f'distances_{suffix}.txt'))
#         elif basename.startswith('distances') and basename != f'distances_{suffix}.txt':
#             os.rename(path, path.replace(basename, f'distances_{suffix}.txt'))
#
#
# def check_file(path, files, subs=None, save=False):
#     global ZIP_CONTENT
#
#     if subs is None:
#         subs = subj.Files(path, files).subs
#
#     if save:
#         save_output(subs, OUTPUT)
#
#         # remove zip folder contents
#         if isinstance(ZIP_CONTENT, list):
#             print('zipfiles:', ZIP_CONTENT)
#             print('contents:', get_content(path, files))
#
#             for content in get_content(path, files):
#                 print('content:', content)
#                 file = content.split('\\')[-1].split('.')[0]
#                 file = file.replace('_preop', '') if 'preop' in file else file.replace('_postop', '') if 'postop' in file else file
#                 print('file:', file)
#
#                 if file in ZIP_CONTENT:
#                     os.remove(content)
#
#                 ZIP_CONTENT = None
#
#     return subs, struct.create_layout(subs, OUTPUT)
#
#
# def get_content(path, files, basename=False):
#     if isinstance(files, str):
#         return traverse_files(os.path.join(path, files), basename=basename, recursive=True)
#
#     all_files = []
#
#     for file in files:
#         if os.path.isdir(os.path.join(path, file)):
#             all_files += traverse_files(os.path.join(path, file), basename=basename, recursive=True)
#         else:
#             all_files.append(os.path.join(path, file))
#     return all_files
#
#
# def save_output(subs, output):
#     if not os.path.exists(output):
#         os.mkdir(output)
#
#     # verify there are no conflicting folders
#     conflict = len(os.listdir(output)) > 0
#
#     def save(sub):
#         for k, v in sub.items():
#             if k in ['weights.txt', 'distances.txt', 'tract_lengths.txt',
#                      'weights_preop.txt', 'distances_preop.txt', 'tract_lengths_preop.txt',
#                      'weights_postop.txt', 'distances_postop.txt', 'tract_lengths_postop.txt']:
#                 wdc.save(sub[k], output)
#             elif k in ['centres.txt', 'centres_preop.txt', 'centres_postop.txt']:
#                 wdc.save(sub[k], output, center=True)
#             elif k.endswith('.mat'):
#                 mat.save(sub[k], output)
#             elif k.endswith('.h5'):
#                 h5.save(sub[k], output)
#
#     # overwrite existing content
#     if conflict:
#         pn.state.notifications.info('Output folder contains files. Removing them...', duration=DURATION)
#         utils.rm_tree(output)
#         prep.reset_index()
#
#     # verify folders exist
#     struct.check_folders(output)
#
#     # save output files
#     for _, val in subs.items():
#         save(val)
#
#
# def create_sub_struct(path, subs):
#     sub = os.path.join(path, f"sub-{subs['sid']}")
#     net = os.path.join(sub, 'net')
#     spatial = os.path.join(sub, 'spatial')
#     ts = os.path.join(sub, 'ts')
#
#     for folder in [sub, net, spatial, ts]:
#         if not os.path.exists(folder):
#             print(f'Creating folder `{folder}`')
#             os.mkdir(folder)
#
#     return sub, net, spatial, ts
#
#
# def get_shape(file, sep):
#     return pd.read_csv(file, sep=sep, index_col=None, header=None).shape
#
#
# def to_tsv(path, file=None):
#     if file is None:
#         Path(path).touch()
#     else:
#         params = {'sep': '\t', 'header': None, 'index': None}
#         pd.DataFrame(file).to_csv(path, **params)
#
#
# def to_json(path, shape, desc, ftype, coords=None):
#     json_file = None
#
#     if ftype == 'simulations':
#         json_file = temp.merge_dicts(temp.JSON_template, temp.JSON_simulations)
#     elif ftype == 'centers':
#         json_file = temp.JSON_centers
#     elif ftype == 'wd':
#         json_file = temp.JSON_template
#
#     if json_file is not None:
#         with open(path, 'w') as f:
#             json.dump(temp.populate_dict(json_file, shape=shape, desc=desc, coords=coords), f)
