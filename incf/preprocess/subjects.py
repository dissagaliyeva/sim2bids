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
        self.files = files
        self.subs = OrderedDict()

        # get all files' absolute paths
        self.content = conv.get_content(path, files)

        # get all files' unique names
        self.basename = set(conv.get_content(path, files, basename=True))

        # check for multi-subject in one folder
        self.match = find_matches(self.basename)

        # check if the input is for single-subject or multi-subject
        conv.MULTI_INPUT = not self.check_input()

        #
        self.ses_found = False

        # traverse folders
        self.traverse_files()

    def check_input(self):
        # simple check counting set literals
        if len(self.content) == len(self.basename):
            # check for multi-subject in one folder
            if len(self.match) == 0:
                return True
            return False
        return False

    def traverse_files(self):
        global TO_RENAME

        # if the whole folder is passed, open that folder
        path, files = self.path, self.files

        if len(files) == 1 and os.path.isdir(os.path.join(path, files[0])) and files[0] not in ['ses-preop',
                                                                                                'ses-postop']:
            path = os.path.join(path, files[0])
            files = os.listdir(path)

        # traverse multi-subject inputs
        if conv.MULTI_INPUT:
            # traverse multi-subject in one folder structure
            if len(self.match) > 0:
                for k, v in get_unique_subs(self.match, self.content).items():
                    # create a new ID
                    sid = self.create_sid_sub()
                    self.subs[sid].update(prepare_subs([os.path.join(path, x) for x in v], sid))
            else:
                # traverse over the provided files
                for file in files:
                    # create a new ID
                    sid = self.create_sid_sub()
                    self.save_sessions('ses-preop', files, sid, path, file)
                    self.save_sessions('ses-postop', files, sid, path, file)

                    if 'ses-preop' not in files and 'ses-postop' not in files:
                        self.subs[sid] = prepare_subs(conv.get_content(path, file), sid)

        else:
            # check if there are no folders inside
            sid = self.create_sid_sub()
            self.save_sessions('ses-preop', files, sid, os.path.join(path, 'ses-preop'))
            self.save_sessions('ses-postop', files, sid, os.path.join(path, 'ses-postop'))

            if not self.ses_found:
                self.create_sid_sub(sid)
                self.subs[sid] = prepare_subs(conv.get_content(path, files), sid)

    def save_sessions(self, ses, files, sid, path, file=None):
        if ses in files:
            self.ses_found = True
            if ses not in self.subs[sid]:
                self.subs[sid][ses] = OrderedDict()

            if file is not None:
                self.subs[sid][ses].update(prepare_subs(conv.get_content(os.path.join(path, file), ses), sid))

    def create_sid_sub(self, sid=None):
        sid = prep.create_uuid() if sid is None else sid

        # create a dictionary to store values
        if sid not in self.subs.keys():
            self.subs[sid] = {}

        return sid


def traverse_single(path, selected, sid, ses=None):
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
