import os
import pandas as pd

from incf.convert import convert as conv


def save_coords(subs: dict, output: str, folders, ses=None):
    template = '{}_desc-{}_{}.{}'
    sid, desc, name = subs['sid'], subs['desc'], subs['name']

    # get path
    path = os.path.join(folders[4], template.format(sid, desc, name, 'tsv'))

    # to tsv
    conv.to_tsv(path, subs['path'])

    # to json
    # file = pd.read_csv(subs['path'], sep='\n', index_col=None, header=None)
    file = pd.DataFrame(open(subs['path'])).apply(lambda x: x.str.strip('\n'))

    conv.to_json(path=path.replace('tsv', 'json'), shape=file.shape, desc=desc, ftype='centers')



