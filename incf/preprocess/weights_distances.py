import os
from pathlib import Path

import pandas as pd
from incf.convert import convert


def save(subs: dict, output: str, folders: list, center: bool = False, ses=None):
    if center:
        # convert.create_sub_struct(output, subs, ses=False)
        save_centers(subs, output, folders, ses=ses)
    else:
        # convert.create_sub_struct(output, subs, ses=True, ses_name=ses)
        save_wd(subs, folders, ses=ses)


def save_wd(subs, folders, ses=None):
    # check and create folders & return paths to them
    if ses is None:
        if convert.CENTERS:
            coords = [f'../coord/desc-{subs["desc"]}_labels.json', f'../coord/desc-{subs["desc"]}_nodes.json']
            save_files(folders, subs, coords)
    else:
        save_files(folders, subs)


def save_files(folders, subs, coords=None):
    DEFAULT_TMPL = '{}_desc-{}_{}.{}'
    name = DEFAULT_TMPL.format(subs['sid'], subs['desc'], subs['name'], 'tsv')
    file = read_csv(subs['path'], subs['sep'])

    if len(folders) == 4:
        net = folders[1]
        save_txt(net, file, name, coords)
    else:
        save_txt(folders[2], file, name, coords)


def save_txt(path, f, name, coords=None):
    if isinstance(f, str):
        Path(os.path.join(path, name)).touch()
        Path(os.path.join(path, name.replace('tsv', 'json'))).touch()

    else:
        # save to tsv
        convert.to_tsv(os.path.join(path, name), f[:])
        convert.to_json(os.path.join(path, name.replace('tsv', 'json')), f.shape,
                        desc='', ftype='wd', coords=coords)


def save_centers(subs, output, folders, ses=None):
    COORD_TMPL = 'desc-{}_{}.{}'
    file = read_csv(subs['path'], subs['sep'])
    labels, nodes = file[0], file[[1, 2, 3]]
    desc = subs['desc']

    lname = COORD_TMPL.format(desc, 'labels', 'tsv')
    nname = COORD_TMPL.format(desc, 'nodes', 'tsv')

    output = output if ses is None else folders[-2]

    if ses is None:
        # save to tsv
        convert.to_tsv(os.path.join(output, 'coord', lname), labels)
        convert.to_tsv(os.path.join(output, 'coord', nname), nodes)

        # save to json
        for content in ['labels', 'nodes']:
            cols = 1 if content == 'labels' else 3
            convert.to_json(os.path.join(output, 'coord', COORD_TMPL.format(desc, content, 'json')),
                            [labels.shape[0], cols], 'Time steps of the simulated time series.', 'centers')
    else:
        convert.to_tsv(os.path.join(output, lname), labels)
        convert.to_tsv(os.path.join(output, nname), nodes)

        # save to json
        for content in ['labels', 'nodes']:
            cols = 1 if content == 'labels' else 3
            convert.to_json(os.path.join(output, COORD_TMPL.format(desc, content, 'json')),
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
