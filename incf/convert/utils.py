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
        self.traverse_files()

    def traverse_files(self):
        if not self.single:
            for file in self.files:
                if os.path.isdir(os.path.join(self.path, file)):
                    sid = prep.create_uuid()
                    self.subs[sid] = conv.prepare_subs(conv.get_content(self.path, file), sid)

        else:
            sid = prep.create_uuid()
            self.subs[sid] = conv.prepare_subs(conv.get_content(self.path, self.files), sid)

        print(self.subs)
