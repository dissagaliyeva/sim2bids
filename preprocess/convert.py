import os
import re
import glob
import json
from scipy.io import loadmat




class Lookup:
    def __init__(self, path='../data'):
        self.path = path

        # empty lists to store found file extensions
        self.dcms = []              # Dicom files
        self.txts = []              # Text files
        self.mats = []              # MATLAB files
        self.eegs = []              # EEG files
        self.imgs = []              # Docker files

        # store all found files
        self.files = []

        # store directories
        self.dirs = []

    def lookup(self):
        files = [x for x in os.listdir(self.path) if not x.startswith('.')]

        for file in files:
            # path =
            if os.path.isdir(os.path.join(self.path, file)):
                self.dirs.append(file)
            # if

        print(files)
        print(self.dirs)


look = Lookup()
look.lookup()