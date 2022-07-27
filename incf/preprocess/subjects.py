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

        print(conv.MULTI_INPUT)

        # traverse files and create subjects
        self.traverse_files()

    def traverse_files(self):
        # traverse multi-folder input
        if conv.MULTI_INPUT:
            files = self.selected_files
            changed_path = False

            # Step 1: change directory to the folders if only one folder is listed
            if len(self.selected_files) == 1:
                changed_path = True
                files = os.listdir(os.path.join(self.path, self.selected_files[0]))

            # Step 1: traverse over the provided input
            for file in files:
                # Step 2: create individual ID; if it already has BIDS format, leave it as is but remove 'sub-'
                sid = prep.create_uuid() if len(re.findall('[0-9]{2,}', file)) == 0 else file

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

                # Step 6: traverse ses-preop if present
                if 'ses-preop' in all_files:
                    self.subs[sid].update(prepare_subs(conv.get_content(path, 'ses-preop'), sid))
                # Step 7: traverse ses-postop if present
                if 'ses-postop' in all_files:
                    self.subs[sid].update(prepare_subs(conv.get_content(path, 'ses-postop'), sid))
                # Step 8: if there are no `ses-preop` and `ses-postop`, traverse the folders as usual
                if 'ses-preop' not in all_files and 'ses-postop' not in all_files:
                    if changed_path:
                        path = path.replace(file, '')

                    if not os.path.exists(os.path.join(path, file)):
                        self.subs[sid] = prepare_subs(conv.get_content(self.path, file), sid)
                    else:
                        self.subs[sid] = prepare_subs(conv.get_content(path.replace(file, ''), file), sid)

        # traverse over single-subject and multi-subject in one folder structure
        else:
            # Step 1: check if the structure contains multi-subject
            pass


def prepare_subs(file_paths, sid):
    subs = {}

    accepted = ['tract_lengths.txt', 'weights.txt', 'centres.txt',
                'tract_lengths_preop.txt', 'weights_preop.txt', 'centres_preop.txt',
                'tract_lengths_postop.txt', 'weights_postop.txt', 'centres_postop.txt',
                'distances.txt', 'distances_preop.txt', 'distances_postop.txt']

    for file_path in file_paths:
        name = get_filename(file_path)
        desc = convert.DESC + 'h5' if file_path.endswith('h5') else convert.DESC

        subs[name] = {
            'name': name.split('.')[0],
            'fname': name,
            'sid': sid,
            'desc': desc,
            'sep': find_separator(file_path),
            'path': file_path,
            'ext': get_file_ext(file_path),
        }

        if subs[name]['name'] in ['tract_lengths', 'tract_lengths_preop', 'tract_lengths_postop']:
            subs[name]['name'] = 'distances'
        if subs[name]['name'] in ['centres', 'centers', 'centres_preop', 'centres_postop']:
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
        f = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        pn.state.notifications.error(f'File {os.path.basename(path)} is empty! Creating an empty file...')
        return ''

    sniffer = csv.Sniffer()

    with open(path) as fp:
        try:
            delimiter = sniffer.sniff(fp.read(5000)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(100)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(500)).delimiter

    delimiter = '\s' if delimiter == ' ' else delimiter
    return delimiter

