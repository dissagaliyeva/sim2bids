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
        self.basename = set(conv.traverse_files(path, files, basename=True))
        self.single = len(self.content) == len(self.basename)

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
                    self.subs[sel].update(
                        prepare_subs(conv.get_content(os.path.join(self.path), sel), sid, suffix='preop'))
                if 'ses-postop' in os.listdir(os.path.join(self.path, sel)):
                    self.subs[sel].update(
                        prepare_subs(conv.get_content(os.path.join(self.path), sel), sid, suffix='postop'))

        else:
            sid = prep.create_uuid()
            self.subs[sid] = prepare_subs(conv.get_content(self.path, self.files), sid)


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
            nsuffix = name.split('.')[0] + suffix
            n = nsuffix + '.' + name.split('.')[1]
        else:
            nsuffix = name.split('.')[0]
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
            subs[n]['name'] = f'distances{suffix}'
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
    if path.split('.')[-1] in ['mat', 'zip', 'h5']:
        return
    print('sep path:', path)
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

# import os
# import csv
# import re
#
# import pandas as pd
#
# from incf.convert import convert
# import os
# from collections import OrderedDict
# import incf.preprocess.preprocess as prep
# import incf.convert.convert as conv
#
# import panel as pn
#
#
# class Files:
#     def __init__(self, path, files):
#         self.path = path
#         self.files = files
#         self.subs = OrderedDict()
#
#         # decide whether input files are for one or more patients
#         self.content = conv.get_content(path, files)
#         self.basename = set(conv.traverse_files(path, files, basename=True))
#         self.single = len(self.content) == len(self.basename)
#
#         print(self.content)
#         # set multi-subject input to true
#         conv.MULTI_INPUT = False if self.single else True
#         self.traverse_files()
#
#     def traverse_files(self):
#         # folder structure inputs
#         if conv.MULTI_INPUT:
#
#             for sel in self.files:
#                 sid = prep.create_uuid() if 'sub-' not in sel else sel.replace('sub-', '')
#                 suffix = None
#                 sel_path = os.path.join(self.path, sel)
#                 print(sel_path, end='\n\n\n')
#
#                 if sel not in self.subs.keys():
#                     self.subs[sid] = {}
#
#                 if 'ses-preop' in os.listdir(sel_path):
#                     suffix = 'preop'
#                     # print(prepare_subs(conv.get_content(self.path, sel), sid, suffix=suffix), end='\n\n\n')
#
#                     self.subs[sid].update(prepare_subs(conv.get_content(self.path, sel, suffix), sid, suffix=suffix))
#                     # conv.remove_files(sel_path, os.listdir(sel_path), suffix)
#                 elif 'ses-postop' in os.listdir(sel_path):
#                     suffix = 'postop'
#                     # print(prepare_subs(conv.get_content(self.path, sel), sid, suffix=suffix), end='\n\n\n')
#                     self.subs[sid].update(prepare_subs(conv.get_content(self.path, sel, suffix), sid, suffix=suffix))
#                 #     conv.remove_files(sel_path, os.listdir(sel_path), suffix)
#                 else:
#                     self.subs[sid] = prepare_subs(conv.get_content(self.path, sel), sid)
#
#         else:
#             sid = prep.create_uuid()
#             self.subs[sid] = prepare_subs(conv.get_content(self.path, self.files), sid)
#
#         print(self.subs)
#
#
# def find_str(path, word, before=True):
#     split = path.find(word) + len(word) + 1
#
#     if before:
#         return path[:split]
#     return path[split:]
#
#
# def prepare_subs(file_paths, sid, suffix=None):
#     print(file_paths)
#     print(sid, end='\n\n')
#     accepted = ['centres.txt', 'weights.txt', 'distances.txt', 'tract_lengths.txt']
#     subs = {}
#     suffix = '' if suffix is None else '_' + suffix
#
#     for file_path in file_paths:
#         name = get_filename(file_path)
#
#         if name.endswith('.DS_Store') or name.endswith('zip'): continue
#         if name.endswith('txt') and name not in accepted: continue
#
#         desc = convert.DESC + 'h5' if file_path.endswith('h5') else convert.DESC
#
#         if not name.split('.')[0].endswith(suffix):
#             nsuffix = name.split('.')[0] + suffix
#             n = nsuffix + '.' + name.split('.')[1]
#         else:
#             nsuffix, n = name, name
#
#         subs[n] = {
#             'name': nsuffix,
#             'fname': name,
#             'sid': sid,
#             'desc': desc,
#             'sep': find_separator(file_path),
#             'path': file_path,
#             'ext': get_file_ext(file_path),
#         }
#
#         if subs[n]['name'] not in subs[n]['path']:
#             new_name = subs[n]['name'] + '.' + subs[n]['ext']
#             new_path = subs[n]['path'].replace(subs[n]['fname'], new_name)
#
#             try:
#                 os.rename(subs[n]['path'], new_path)
#             except FileExistsError:
#                 continue
#             else:
#                 subs[n]['fname'] = new_name
#                 subs[n]['path'] = new_path
#
#                 print('subs[n]["name"]', subs[n]['name'])
#                 if subs[n]['name'] in ['tract_lengths', 'tract_length',
#                                        'tract_lengths_preop', 'tract_lengths_postop']:
#                     subs[n]['name'] = f'distances_{suffix}'
#                 if subs[n]['name'] in ['centres', 'centres_preop', 'centres_postop']:
#                     conv.CENTERS = True
#
#     return subs
#
#
# def get_filename(path):
#     return os.path.basename(path)
#
#
# def get_file_ext(path):
#     return path.split('.')[-1]
#
#
# def find_separator(path):
#     """
#     Find the separator/delimiter used in the file to ensure no exception
#     is raised while reading files.
#
#     :param path:
#     :return:
#     """
#     if path.split('.')[-1] in ['mat', 'zip', 'h5']:
#         return
#
#     try:
#         f = pd.read_csv(path)
#     except pd.errors.EmptyDataError:
#         pn.state.notifications.error(f'File {os.path.basename(path)} is empty! Creating an empty file...')
#         return ''
#
#     sniffer = csv.Sniffer()
#
#     with open(path) as fp:
#         try:
#             delimiter = sniffer.sniff(fp.read(5000)).delimiter
#         except Exception:
#             delimiter = sniffer.sniff(fp.read(100)).delimiter
#         except:
#             delimiter = sniffer.sniff(fp.read(500)).delimiter
#
#     delimiter = '\s' if delimiter == ' ' else delimiter
#     return delimiter
