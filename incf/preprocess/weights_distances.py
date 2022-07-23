import os
from pathlib import Path

import pandas as pd
from incf.convert import convert


def save(subs: dict, output: str, center: bool = False):
    if center:
        save_centers(subs, output)
    else:
        save_wd(subs, output)


def save_wd(subs, output):
    DEFAULT_TMPL = 'sub-{}_desc-{}_{}.{}'
    # check and create folders & return paths to them
    sub, net, spatial, ts = convert.create_sub_struct(output, subs)

    name = DEFAULT_TMPL.format(subs['sid'], subs['desc'], subs['name'], 'tsv')
    file = read_csv(subs['path'], subs['sep'])

    # add coordinates if exists
    coords = None

    if convert.CENTERS:
        coords = [f'../coord/desc-{subs["desc"]}_labels.json', f'../coord/desc-{subs["desc"]}_nodes.json']

    if isinstance(file, str):
        Path(os.path.join(net, name)).touch()
        Path(os.path.join(net, name.replace('tsv', 'json'))).touch()

    else:
        # save to tsv
        convert.to_tsv(os.path.join(net, name), file[:])
        convert.to_json(os.path.join(net, name.replace('tsv', 'json')), file.shape, desc='', ftype='wd', coords=coords)


def save_centers(subs, output):
    COORD_TMPL = 'desc-{}_{}.{}'
    file = read_csv(subs['path'], subs['sep'])
    labels, nodes = file[0], file[[1, 2, 3]]
    desc = subs['desc']

    lname = COORD_TMPL.format(desc, 'labels', 'tsv')
    nname = COORD_TMPL.format(desc, 'nodes', 'tsv')

    # save to tsv
    convert.to_tsv(os.path.join(output, 'coord', lname), labels)
    convert.to_tsv(os.path.join(output, 'coord', nname), nodes)

    # save to json
    for content in ['labels', 'nodes']:
        cols = 1 if content == 'labels' else 3
        convert.to_json(os.path.join(output, 'coord', COORD_TMPL.format(desc, content, 'json')),
                        [labels.shape[0], cols], 'Time steps of the simulated time series.', 'centers')


def read_csv(path, sep):
    try:
        f = pd.read_csv(path, sep=sep, header=None, index_col=False)
    except pd.errors.EmptyDataError:
        return ''
    except ValueError:
        return ''
    else:
        return f
