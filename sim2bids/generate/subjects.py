import os
import csv
import re
from pathlib import Path

import pandas as pd

from sim2bids.app import app
from collections import OrderedDict
import sim2bids.preprocess.preprocess as prep
from sim2bids.convert import convert
from sim2bids.app import utils


class Files:
    def __init__(self, path, files):
        self.path = path
        self.files = files
        self.subs = OrderedDict()

        # get all files' absolute paths
        self.content = utils.get_content(path, files)

        # get all files
        app.ALL_FILES = self.content

        # get all files' unique names
        self.basename = set(utils.get_content(path, files, basename=True))

        # check for multi-subject in one folder
        self.match = find_matches(self.basename)

        # check if the input is for single-subject or multi-subject
        app.MULTI_INPUT = not self.check_input()

        # define a variable that is going to check whether input
        # contains sessions-based subject. Sessions include `ses-preop` and 'ses-postop'
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
        # if the whole folder is passed, open that folder
        path, files, changed = self.path, self.files, False

        if len(files) == 1 and os.path.isdir(os.path.join(path, files[0])) and files[0] not in ['ses-preop', 'ses-postop']:
            path = os.path.join(path, files[0])
            files = os.listdir(path)

        # traverse multi-subject inputs
        if app.MULTI_INPUT:
            # traverse multi-subject in one folder structure
            if len(self.match) > 0:
                for k, v in get_unique_subs(self.match, self.content).items():
                    # create a new ID
                    sid = self.create_sid_sub()
                    self.subs[sid].update(prepare_subs([os.path.join(path, x) for x in v], sid))
            else:
                for file in files:
                    sid = self.create_sid_sub()

                    # Step 5: get all content
                    all_files = os.listdir(path)

                    # Step 6: traverse ses-preop if present
                    if 'ses-preop' in all_files:
                        self.save_sessions('ses-preop', all_files, sid, path)

                    # Step 7: traverse ses-postop if present
                    if 'ses-postop' in all_files:
                        self.save_sessions('ses-postop', all_files, sid, path)

                    if 'ses-preop' not in all_files and 'ses-postop' not in all_files:
                        if os.path.basename(path) == file:
                            self.subs[sid] = prepare_subs(utils.get_content(path.replace(file, ''), file), sid)
                        else:
                            self.subs[sid] = prepare_subs(utils.get_content(path, file), sid)

        else:
            # check if there are no folders inside
            sid = self.create_sid_sub()
            self.save_sessions('ses-preop', files, sid, os.path.join(path, 'ses-preop'))
            self.save_sessions('ses-postop', files, sid, os.path.join(path, 'ses-postop'))

            if not self.ses_found:
                self.create_sid_sub(sid)
                self.subs[sid] = prepare_subs(utils.get_content(path, files), sid)

    def save_sessions(self, ses, files, sid, path):
        if ses in files:
            self.ses_found = True
            if sid not in self.subs.keys():
                self.subs[sid] = OrderedDict()
            if ses not in self.subs[sid].keys():
                self.subs[sid][ses] = OrderedDict()

            self.subs[sid][ses].update(prepare_subs(utils.get_content(path, ses), sid))

    def create_sid_sub(self, sid=None):
        sid = prep.create_uuid() if sid is None else sid

        # create a dictionary to store values
        if sid not in self.subs.keys():
            self.subs[sid] = {}

        return sid


def traverse_single(path, selected, sid, ses=None):
    if ses is not None:
        return prepare_subs(utils.get_content(path, ses), sid)
    else:
        return prepare_subs(utils.get_content(path, selected), sid)


def find_matches(paths):
    unique_ids = []

    for path in paths:
        match = re.findall('^[A-Za-z]{2,3}_[0-9]{2,}', path)
        if len(match) > 0 and not path.endswith('.h5'):
            unique_ids.append(match[0])

    return list(set(unique_ids))


def get_unique_subs(match, contents):
    subs = OrderedDict()

    for idx in range(len(match)):
        subs[match[idx]] = [x for x in contents if match[idx] in x]

    return subs


def prepare_subs(file_paths, sid):
    subs = {}

    for file_path in file_paths:
        print(file_path)
        name = get_filename(file_path)

        if file_path.endswith('.h5'):
            name = name.split('_')[0] + '.h5'
        else:
            if 'bold' not in name:
                name = name.split('_')[-1] if '_' in name else name
        desc = app.DESC

        # get extensions
        ext = os.path.basename(file_path).split('.')[-1]

        # check if file ends with CSV or dat, if true, change file
        # extension to plain TXT. It's necessary so that there's minimal
        # number of "if" statements in the future traversals
        if ext.endswith('csv') or ext.endswith('dat'):
            # instantiate a new path
            new_path = file_path.replace(ext, 'txt')

            if os.path.exists(file_path):
                p = Path(file_path)
                p.rename(p.with_suffix('.txt'))

                # set the new path
                file_path = new_path

        # rename tract_lengths to distances
        if name == 'tract_lengths.txt':
            name = 'distances.txt'

        if not os.path.exists(file_path) and 'distances' in file_path:
            if os.path.exists(file_path.replace('distances', 'tract_lengths')):
                os.replace(file_path.replace('distances', 'tract_lengths'), file_path)
            else:
                continue

        # rename tract_lengths to distances in the physical folder location
        if 'tract_lengths' in file_path:
            new_path = file_path.replace('tract_lengths', 'distances')
            os.replace(file_path, new_path)
            file_path = new_path

        # rename average_orientations to normals in both subject- and physical levels
        if name in ['average_orientations.txt', 'orientations.txt']:
            name = 'normals.txt'
            new_path = file_path.replace(name.replace('.txt', ''), 'normals')
            os.replace(file_path, new_path)
            file_path = new_path

        # check if separator is missing, if so remove the file entirely
        if accepted(name):
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

            if subs[name]['name'] in ['centres', 'centre']:
                app.CENTERS = True

            # save network path
            if len(convert.NETWORK) < 2:
                desc, fname = app.DESC, name.split('.')[0]

                if fname in ['weights', 'distances']:
                    if 'ses-preop' in subs[name]['path'] in subs[name]['path']:
                        convert.NETWORK.append(f'../{sid}/ses-preop/net/{sid}_desc-{app.DESC}_{fname}.json')
                    elif 'ses-postop' in subs[name]['path'] in subs[name]['path']:
                        convert.NETWORK.append(f'../{sid}/ses-postop/net/{sid}_desc-{app.DESC}_{fname}.json')
                    else:
                        convert.NETWORK.append(f'../{sid}/net/{sid}_desc-{app.DESC}_{fname}.json')

                    convert.NETWORK = list(set(convert.NETWORK))

    return subs


def accepted(name):
    for accept in app.ACCEPTED:
        if accept in name:
            if accept == 'ts' and len(name) == 2:
                return True
            elif accept != 'ts':
                return True

    return False


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
        file = pd.read_csv(path, index_col=None, header=None, sep=' ')
    except pd.errors.EmptyDataError:
        return 'remove'
    except pd.errors.ParserError:
        print(path)


    # if cortical.txt, hemisphere.txt, or areas.txt are present, return '\n' delimiter
    if path.endswith('hemisphere.txt') or path.endswith('cortical.txt') or path.endswith('areas.txt') \
            or path.endswith('times.txt'):
        file.to_csv(path, sep='\n', header=None, index=None)
        return '\n'

    if file.shape[0] > 1 and file.shape[1] > 1:
        return '\s'

    sniffer = csv.Sniffer()

    with open(path) as fp:
        try:
            delimiter = sniffer.sniff(fp.read(5000)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(50)).delimiter

    delimiter = '\s' if delimiter == ' ' else delimiter
    return delimiter
