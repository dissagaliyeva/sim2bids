import os, sys
import pandas as pd
from incf.convert import convert


def save(subs: dict, output: str, center: bool = False):
    if center:
        save_centers(subs, output)
    else:
        save_wd(subs, output)


def save_wd(subs, output):
    # check and create folders & return paths to them
    sub, net, spatial, ts = convert.create_sub_struct(output, subs)

    name = convert.DEFAULT_TMPL.format(subs['sid'], subs['desc'], subs['name'])
    file = read_csv(subs['path'], subs['sep'])

    # save to tsv
    convert.to_tsv(os.path.join(net, name + 'tsv'), file[:])

    # add coordinates if exists
    coords = None

    print(convert.CENTERS)

    if convert.CENTERS:
        coords = [f'../coord/desc-{subs["desc"]}_labels.json', f'../coord/desc-{subs["desc"]}_nodes.json']

    convert.to_json(os.path.join(net, name + 'json'), file.shape, desc='', ftype='wd', coords=coords)


def save_centers(subs, output):
    file = read_csv(subs['path'], subs['sep'])
    labels, nodes = file[0], file[[1, 2, 3]]
    desc = subs['desc']

    lname = convert.COORD_TMPL.format(desc, 'labels', 'tsv')
    nname = convert.COORD_TMPL.format(desc, 'nodes', 'tsv')

    # save to tsv
    convert.to_tsv(os.path.join(output, 'coord', lname), labels)
    convert.to_tsv(os.path.join(output, 'coord', nname), nodes)

    # save to json
    for content in ['labels', 'nodes']:
        cols = 1 if content == 'labels' else 3
        convert.to_json(os.path.join(output, 'coord', convert.COORD_TMPL.format(desc, content, 'json')),
                        [labels.shape[0], cols], 'Time steps of the simulated time series.', 'centers')


def read_csv(path, sep):
    return pd.read_csv(path, sep=sep, header=None, index_col=False)
