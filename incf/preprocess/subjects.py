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
        if not self.single:
            for file in self.files:
                if os.path.isdir(os.path.join(self.path, file)):
                    sid = prep.create_uuid()
                    self.subs[sid] = prepare_subs(conv.get_content(self.path, file), sid)

        else:
            sid = prep.create_uuid()
            self.subs[sid] = prepare_subs(conv.get_content(self.path, self.files), sid)

        print(self.subs)


def prepare_subs(file_paths, sid):
    desc = convert.DESC

    subs = {}
    for file_path in file_paths:
        name = get_filename(file_path)
        desc = desc + 'h5' if file_path.endswith('h5') else desc

        subs[name] = {
            'fname': name,
            'sid': sid,
            'sep': find_separator(file_path),
            'desc': desc,
            'path': file_path,
            'ext': get_file_ext(file_path),
            'name': name.split('.')[0]
        }

        if subs[name]['name'] in ['tract_lengths', 'tract_length']:
            subs[name]['name'] = 'distances'
        if subs[name]['name'] == 'centres':
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
