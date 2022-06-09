import os
import re
import glob
import json
from scipy.io import loadmat


def convert_mat(path: str = '../data') -> str:
    files = os.listdir(path)


def lookup(path: str):
    files = [x for x in os.listdir(path) if not x.startswith('.')]

    # store directories
    dirs = []

    for file in files:
        if os.path.isdir(os.path.join(path, file)):
            print(f'found folder: {file}')


lookup('C:/Users/wwwxd/Desktop/incf')
