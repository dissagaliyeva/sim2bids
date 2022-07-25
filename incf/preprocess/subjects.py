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
        self.files = files
        self.subs = OrderedDict()

        # decide whether input files are for one or more patients
        self.content = conv.get_content(path, files)
        print('self.content:', self.content, end='\n\n')
        self.basename = set(conv.traverse_files(path, files, basename=True))
        self.single = len(self.content) == len(self.basename)
        print('self.single:', self.single)

        # set multi-subject input to true
        conv.MULTI_INPUT = False if self.single else True
        self.traverse_files()

    def traverse_files(self):
        # folder structure inputs
        if conv.MULTI_INPUT:
            for sel in self.files:
                sid = prep.create_uuid() if re.findall('[0-9]+', sel) == 0 else sel.replace('sub-', '')

                if sel not in self.subs.keys():
                    self.subs[sel] = {}

                if 'ses-preop' in os.listdir(os.path.join(self.path, sel)):
                    content = conv.get_content(os.path.join(self.path), sel)
                    conv.verify_zip_files(content)
                    self.subs[sel].update(
                        prepare_subs(conv.get_content(os.path.join(self.path), sel), sid, suffix='preop'))
                elif 'ses-postop' in os.listdir(os.path.join(self.path, sel)):
                    content = conv.get_content(os.path.join(self.path), sel)
                    conv.verify_zip_files(content)

                    self.subs[sel].update(
                        prepare_subs(conv.get_content(os.path.join(self.path), sel), sid, suffix='postop'))
                else:
                    self.subs[sel] = prepare_subs(conv.get_content(self.path, sel), sel)

        else:
            sid = prep.create_uuid()
            self.subs[sid] = prepare_subs(self.content, sid)


def find_str(path, word, before=True):
    split = path.find(word) + len(word) + 1

    if before:
        return path[:split]
    return path[split:]


def prepare_subs(file_paths, sid, suffix=None):
    subs = {}
    suffix = '' if suffix is None else '_' + suffix
    accepted = ['tract_lengths.txt', 'weights.txt', 'centres.txt',
                'tract_lengths_preop.txt', 'weights_preop.txt', 'centres_preop.txt',
                'tract_lengths_postop.txt', 'weights_postop.txt', 'centres_postop.txt',
                'distances.txt', 'distances_preop.txt', 'distances_postop.txt']

    for file_path in file_paths:

        if file_path.endswith('txt') and get_filename(file_path) not in accepted:
            continue
        name = get_filename(file_path)
        desc = convert.DESC + 'h5' if file_path.endswith('h5') else convert.DESC

        if 'preop' in name or 'postop' in name:
            nsuffix = name.split('.')[0]
        else:
            nsuffix = name.split('.')[0] + suffix

        n = nsuffix + '.' + name.split('.')[1]

        subs[n] = {
            'name': nsuffix,
            'fname': name,
            'sid': sid,
            'desc': desc,
            'sep': find_separator(file_path),
            'path': file_path,
            'ext': get_file_ext(file_path),
        }

        if subs[n]['name'] in ['tract_lengths', 'tract_length',
                               'tract_lengths_preop', 'tract_length_preop',
                               'tract_lengths_postop', 'tract_length_postop']:
            subs[n]['name'] = f'distances_preop' if 'preop' in name else 'distances_postop' \
                if 'postop' in name else 'distances'
        if subs[n]['name'] in ['centres', 'centers', 'centres_preop', 'centres_postop']:
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
