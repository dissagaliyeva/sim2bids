import os
import csv
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
        self.basename = set(conv.traverse_files(path, basename=True))
        self.single = len(self.content) == len(self.basename)

        # set multi-subject input to true
        conv.MULTI_INPUT = False if self.single else True
        self.traverse_files()

    def traverse_files(self):
        # folder structure inputs
        if not self.single:
            main_folder = os.path.basename(self.path)

            for file in self.files:
                if os.path.isdir(os.path.join(self.path, file)):
                    sid = prep.create_uuid()
                    contents = conv.get_content(self.path, file)

                    # traverse content
                    for content in contents:
                        # get path after the main folder
                        path = find_str(content, main_folder, before=False)

                        # split the folder to get individual file/folder
                        split = path.split('\\')
                        s0, s1 = split[0], split[1]

                        # add new key
                        if s0 not in self.subs:
                            self.subs[s0] = {}

                        if os.path.isdir(find_str(content, s1)) and s1 not in self.subs[s0]:
                            self.subs[s0][s1] = []

                        self.subs[s0][s1].append(os.path.basename(content))

        else:
            sid = prep.create_uuid()
            self.subs[sid] = prepare_subs(conv.get_content(self.path, self.files), sid)


def find_str(path, word, before=True):
    split = path.find(word) + len(word) + 1

    if before:
        return path[:split]
    return path[split:]


def prepare_subs(file_paths, sid):
    subs = {}

    for file_path in file_paths:
        name = get_filename(file_path)
        desc = convert.DESC + 'h5' if file_path.endswith('h5') else convert.DESC

        subs[name] = {
            'fname': name,
            'sid': sid,
            'desc': desc,
            'path': file_path,
            'ext': get_file_ext(file_path),
            'name': name.split('.')[0]
        }

        name = subs[name]['name']

        if name.endswith('txt') or name.endswith('.csv'):
            subs[name]['sep'] = find_separator(file_path)

        if name in ['tract_lengths', 'tract_length']:
            subs[name]['name'] = 'distances'
        if name == 'centres':
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

    if path.endswith('.mat') or path.endswith('.h5'):
        return

    sniffer = csv.Sniffer()

    with open(path) as fp:
        try:
            delimiter = sniffer.sniff(fp.read(5000)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(100)).delimiter

    delimiter = '\s' if delimiter == ' ' else delimiter
    return delimiter
