import os
from pathlib import Path

import pandas as pd
from incf.convert import convert
from incf.preprocess import weights_distances as wd

DEFAULT_TMPL = '{}_desc-{}_{}.{}'


def save(sub, output, folders, end, ses=None):
    if ses is None:
        if end == 'map.txt':
            wd.save_files(folders, sub, idx=2)
        else:
            wd.save_files(folders, sub, idx=-1)
    else:
        if end == 'map.txt':
            wd.save_files(folders, sub, idx=3)
        else:
            wd.save_files(folders, sub, idx=-1)
