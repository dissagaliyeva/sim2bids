import os
import pandas as pd

from incf.convert import convert as conv


def save_coords(subs: dict, folders):
    template = '{}_desc-{}_{}.{}'
    sid, desc, name = subs['sid'], subs['desc'], subs['name']

    # get path
    path = os.path.join(folders[4], template.format(sid, desc, name, 'tsv'))

    # to tsv
    conv.to_tsv(path, subs['path'], sep=subs['sep'])

    # to json
    file = pd.DataFrame(open(subs['path'])).apply(lambda x: x.str.strip('\n'))

    conv.to_json(path=path.replace('tsv', 'json'), shape=file.shape, desc=desc, ftype='centers', key='coord')



