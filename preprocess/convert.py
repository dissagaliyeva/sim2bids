import os
import re
import glob
import json
import logging
from scipy.io import loadmat

import numpy as np
import pandas as pd


class Lookup:
    def __init__(self, path='data', limit=3, output='output'):
        self.path   = self.find_path(path, limit=limit)
        self.output = output

        # define extensions
        self.extensions = ['.mat', '.dcm', '.txt', '.img', '.eeg']

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

    def find_path(self, path, limit=3, idx=0):
        """Recursively find path by traversing parent directory LIMIT times"""

        # base case = raise error if not limit reached
        if limit == idx:
            raise ValueError(f'No folder `{path}` present in all {limit} levels.')

        # return path if found
        if os.path.exists(path):
            return path

        # update index and file location
        idx += 1
        path = os.path.join('..', path)

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


look = Lookup()
look.lookup()
print(look.path)
print(look.eegs, look.imgs, look.txts, look.mats, look.dcms)


def to_tsv(val, output='../output'):
    # create folder if not present
    if not os.path.exists(output):
        print(f'Creating folder `{output}`')
        os.mkdir(output)

    def mat_to_csv(mat_path):
        assert os.path.exists(mat_path), f'`{mat_path}` does not exist.'
        mat = loadmat(mat_path)
        f_name = os.path.join(output, os.path.splitext(os.path.basename(mat_path))[0])
        pd.DataFrame(mat['data']).to_csv(os.path.join(output, f_name),
                                         index=False, sep='\t', header=False)

    if isinstance(val, str):
        mat_to_csv(val)
    elif isinstance(val, list):


to_tsv(look.mats)