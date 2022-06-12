import os
import re
import glob
import json
import logging
from scipy.io import loadmat

import numpy as np
import pandas as pd


FILE_EXT = ['.mat', '.txt', '.dcm', '.eeg', '.img', '.py']


class Lookup:
    def __init__(self, path='data', limit=3, output='output'):
        self.path   = self.find_path(path, limit=limit)
        self.output = output

        # define extensions
        self.extensions = FILE_EXT

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

        # get content
        # self.

    def find_path(self, limit=3, idx=0):
        """Recursively find path by traversing parent directory LIMIT times"""

        # base case = raise error if not limit reached
        if limit == idx:
            raise ValueError(f'No folder `{self.path}` present in all {limit} levels.')

        # return path if found
        if os.path.exists(self.path):
            print(f'Data found in `{self.path}` at level {idx}')
            return self.path

        # update index and file location
        idx += 1
        path = os.path.join('..', self.path)

        # recursively call function
        return self.find_path(path, idx=idx)

    def lookup(self):
        files = [x for x in os.listdir(self.path) if not x.startswith('.')]

        for file in files:
            path = os.path.join(self.path, file)
            if os.path.isdir(path):
                self.dirs.append(file)
            elif path[-4:] in self.extensions:
                # append the file
                self.files.append(path)

                if path.endswith('.mat'):
                    self.mats.append(path)
                elif path.endswith('.dcm'):
                    self.dcms.append(path)
                elif path.endswith('.txt'):
                    self.txts.append(path)
                elif path.endswith('.eeg'):
                    self.eegs.append(path)
                elif path.endswith('.img'):
                    self.imgs.append(path)

        if self.dirs:
            print('Found folders:', self.dirs)
            # TODO: add recursive folder lookup



# look = Lookup()
# look.lookup()
# print(look.path)
# print(look.eegs, look.imgs, look.txts, look.mats, look.dcms)
