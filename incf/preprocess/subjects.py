import os
import csv
import re

import pandas as pd
import panel as pn

from incf.convert import convert
import os
from collections import OrderedDict
import incf.preprocess.preprocess as prep
import incf.convert.convert as conv

TO_RENAME = None


class Files:
    def __init__(self, path, files):
        self.path = path
        self.selected_files = files
        self.subs = OrderedDict()

        # decide whether input files are for one or more patients
        self.content = conv.get_content(path, files)
        self.basename = set(conv.get_content(path, files, basename=True))
        self.single = len(self.content) == len(self.basename)

        # set multi-subject input to true
        conv.MULTI_INPUT = False if self.single else True
        conv.ALL_FILES = self.content

        # traverse files and create subjects
        self.traverse_files()

    def traverse_files(self):
        global TO_RENAME

        # traverse multi-folder input
        if conv.MULTI_INPUT:

            files = self.selected_files
            changed_path = False

            # Step 1: change directory to the folders if only one folder is listed
            if len(self.selected_files) == 1:
                if len(set(os.listdir(os.path.join(self.path, self.selected_files[0]))).intersection(
                        {'ses-preop', 'ses-postop'})) == 0:
                    changed_path = True
                    files = os.listdir(os.path.join(self.path, self.selected_files[0]))

            # Step 1: traverse over the provided input
            for file in files:
                # Step 2: create individual ID; if it already has BIDS format, leave it as is but remove 'sub-'
                sid = prep.create_uuid()

                # Step 3: create a dictionary to store values
                if sid not in self.subs.keys():
                    self.subs[sid] = {}

                # Step 4: change path to the files
                if changed_path:
                    path = os.path.join(self.path, self.selected_files[0], file)
                else:
                    path = os.path.join(self.path, file)

                # Step 5: get all content
                all_files = os.listdir(path)
                conv.ALL_FILES = all_files

                # Step 6: traverse ses-preop if present
                if 'ses-preop' in all_files:
                    if 'ses-preop' not in self.subs[sid]:
                        self.subs[sid]['ses-preop'] = OrderedDict()

                    self.subs[sid]['ses-preop'].update(prepare_subs(conv.get_content(path, 'ses-preop'), sid))

                # Step 7: traverse ses-postop if present
                if 'ses-postop' in all_files:
                    if 'ses-postop' not in self.subs[sid]:
                        self.subs[sid]['ses-postop'] = OrderedDict()

                    self.subs[sid]['ses-postop'].update(prepare_subs(conv.get_content(path, 'ses-postop'), sid))

                if 'ses-preop' not in all_files and 'ses-postop' not in all_files:
                    self.subs[sid] = prepare_subs(conv.get_content(self.path, file), sid)

        # traverse over single-subject and multi-subject in one folder structure
        else:
            sid = prep.create_uuid()

            # Step 1: check if the structure contains multi-subject
            match = find_matches(self.basename)
            # traverse multi-subject in one folder
            if len(match) > 0:
                convert.MULTI_INPUT = True
                # get unique IDs for matches
                TO_RENAME = get_extensions(self.basename, match)
                for k, v in get_unique_subs(match, self.content).items():
                    sid = prep.create_uuid()
                    if sid not in self.subs.keys():
                        self.subs[sid] = {}
                    if len(self.selected_files) == 1:
                        self.subs[sid].update(
                            prepare_subs([os.path.join(self.path, self.selected_files[0], x) for x in v], sid))
                    else:
                        self.subs[sid].update(prepare_subs([os.path.join(self.path, x) for x in v], sid))

            else:
                sessions, path = [], None

                # check if a folder with folders is passed
                if len(self.selected_files) == 1:
                    path = os.path.join(self.path, self.selected_files[0])
                    contents = os.listdir(path)

                    # check if session-specific folders are passed
                    if 'ses-preop' in contents:
                        sessions.append('ses-preop')
                    elif 'ses-postop' in contents:
                        sessions.append('ses-postop')

                if len(self.selected_files) == 1 and os.path.isdir(os.path.join(self.path, self.selected_files[0])):
                    if len(sessions) == 0:
                        self.subs[sid] = traverse_single(self.path, self.selected_files[0], sid)
                    else:
                        if sid not in self.subs.keys():
                            self.subs[sid] = {'ses-preop': {}, 'ses-postop': {}}

                        for session in sessions:
                            if path is None:
                                self.subs[sid][session] = traverse_single(self.path, self.selected_files, sid,
                                                                          ses=session)
                            else:
                                self.subs[sid][session] = traverse_single(path, self.selected_files, sid, ses=session)
                else:
                    self.subs[sid] = traverse_single(self.path, self.selected_files, sid)


def traverse_single(path, selected, sid, ses='ses-preop'):
    if ses is not None:
        return prepare_subs(conv.get_content(path, ses), sid)
    else:
        return prepare_subs(conv.get_content(path, selected), sid)


def find_matches(paths):
    unique_ids = []

    for path in paths:
        match = re.findall('^[A-Za-z]{2,}_[0-9]{2,}', path)
        if len(match) > 0:
            unique_ids.append(match[0])

    return list(set(unique_ids))


def get_unique_subs(match, contents):
    subs = OrderedDict()

    for idx in range(len(match)):
        subs[match[idx]] = [x for x in contents if match[idx] in x]

    return subs


def get_extensions(files, ids=None):
    if ids is not None:
        return [x for x in list(set([remove_id(x, ids) for x in files])) if x is not None]


def remove_id(file, ids):
    for id_ in ids:
        if file.startswith(id_):
            return file.replace(id_, '').strip(',.\\/_;!?-')


def prepare_subs(file_paths, sid):
    subs = {}

    for file_path in file_paths:
        name = get_filename(file_path)
        name = name.split('_')[-1] if '_' in name else name
        desc = convert.DESC

        # rename tract_lengths to distances
        if name == 'tract_lengths.txt':
            name = 'distances.txt'

        # rename tract_lengths to distances in the physical folder location
        if 'tract_lengths' in file_path and not os.path.exists(file_path.replace('tract_lengths', 'distances')):
            new_path = file_path.replace('tract_lengths', 'distances')
            os.replace(file_path, new_path)
            file_path = new_path

        # rename average_orientations to normals in both subject- and physical levels
        if name == 'average_orientations.txt':
            name = 'normals.txt'
            new_path = file_path.replace('average_orientations', 'normals')
            os.replace(file_path, new_path)
            file_path = new_path

        # check if separator is missing, if so remove the file entirely
        sep = find_separator(file_path)

        if sep == 'remove':
            os.remove(file_path)
            continue

        subs[name] = {
            'name': name.split('.')[0],
            'fname': name,
            'sid': sid,
            'desc': desc,
            'sep': sep,
            'path': file_path,
            'ext': get_file_ext(file_path),
        }

        if subs[name]['name'] in ['centres', 'centers']:
            conv.CENTERS = True

    return subs


def get_filename(path):
    return os.path.basename(path)


def get_file_ext(path):
    return path.split('.')[-1]


def find_separator(path):
    """
    Find the separator/delimiter used in the file to ensure no exception
    is raised while reading files.
    :param path:
    :return:
    """
    if path.split('.')[-1] not in ['txt', 'csv']:
        return

    try:
        file = pd.read_csv(path, index_col=None, header=None)
    except pd.errors.EmptyDataError:
        pn.state.notifications.error(f'File {os.path.basename(path)} is empty! Removing the file...')
        return 'remove'

    # if cortical.txt, hemisphere.txt, or areas.txt are present, return '\n' delimiter
    if path.endswith('hemisphere.txt') or path.endswith('cortical.txt') or path.endswith('areas.txt'):
        file.to_csv(path, sep='\n', header=None, index=None)
        return '\n'

    sniffer = csv.Sniffer()

    with open(path) as fp:
        try:
            delimiter = sniffer.sniff(fp.read(5000)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(100)).delimiter

    delimiter = '\s' if delimiter == ' ' else delimiter
    return delimiter
