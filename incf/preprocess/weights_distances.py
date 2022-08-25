import os
from pathlib import Path

import pandas as pd
from incf.appert import appert

DEFAULT_TMPL = '{}_desc-{}_{}.{}'


def save(subs: dict, output: str, folders: list, center: bool = False, ses=None):
    if center:
        save_centers(subs, output, folders, ses=ses)
    else:
        save_wd(subs, folders, ses=ses)


def save_wd(subs, folders, ses=None):
    # check and create folders & return paths to them
    if ses is None:
        coords = None

        if appert.CENTERS:
            coords = [f'../coord/desc-{subs["desc"]}_labels.json', f'../coord/desc-{subs["desc"]}_nodes.json']

        save_files(folders, subs, idx=1, coords=coords)
    else:
        save_files(folders, subs, idx=2)


def save_areas(subs, output, ses=None):
    # get subject-specific information
    sid, name, desc, sub_path, sep = subs['sid'], subs['fname'], subs['desc'], subs['path'], subs['sep']

    # get path to "map" folder
    if ses:
        path = os.path.join(output, sid, ses, 'map')
    else:
        path = os.path.join(output, sid, 'map')

    # check if path exists, if no create the folder and add values
    # otherwise ignore to reduce redundancy and overwriting
    if not os.path.exists(path):
        # create the "map" folder if it doesn't exist
        os.mkdir(path)

        # save content
        save_txt(path, read_csv(sub_path, sep), DEFAULT_TMPL.format(subs['sid'], subs['desc'], subs['name'], 'tsv'))


def save_files(folders, subs, idx, coords=None):
    name = DEFAULT_TMPL.format(subs['sid'], subs['desc'], subs['name'], 'tsv')
    file = read_csv(subs['path'], subs['sep'])

    if len(folders) == 4 or len(folders) == 5:
        save_txt(folders[idx], file, name, coords)
    else:
        save_txt(folders[idx], file, name, coords)


def save_txt(path, f, name, coords=None):
    """

    :param path:    Path to the file location
    :param f:       File content, expected to have pd.DataFrame type
    :param name:    Name of the file, expected to have TXT or CSV extension
    :param coords:  Coordinates to nodes/labels location
    :return:
    """
    if isinstance(f, str):
        pass
        # Path(os.path.join(path, name)).touch()
        # Path(os.path.join(path, name.replace('tsv', 'json'))).touch()

    else:
        # save to tsv
        appert.to_tsv(os.path.join(path, name), f[:])
        appert.to_json(os.path.join(path, name.replace('tsv', 'json')), f.shape, desc='', key='wd', coords=coords)


def save_centers(subs, output, folders, ses=None):
    COORD_TMPL = 'desc-{}_{}.{}'
    file = read_csv(subs['path'], subs['sep'])
    labels, nodes = file[0], file.iloc[:, 1:]
    desc = subs['desc']

    lname = COORD_TMPL.format(desc, 'labels', 'tsv')
    nname = COORD_TMPL.format(desc, 'nodes', 'tsv')

    output = output if ses is None else folders[-2]

    if ses is None:
        # save to tsv
        appert.to_tsv(os.path.join(output, 'coord', lname), labels)
        appert.to_tsv(os.path.join(output, 'coord', nname), nodes)

        # save to json
        for content in ['labels', 'nodes']:
            cols = 1 if content == 'labels' else 3
            appert.to_json(os.path.join(output, 'coord', COORD_TMPL.format(desc, content, 'json')),
                            shape=[labels.shape[0], cols], desc='Time steps of the simulated time series.',
                            key='coord')
    else:
        appert.to_tsv(os.path.join(output, subs['sid'] + '_' + lname), labels)
        appert.to_tsv(os.path.join(output, subs['sid'] + '_' + nname), nodes)

        # save to json
        for content in ['labels', 'nodes']:
            cols = 1 if content == 'labels' else 3
            appert.to_json(os.path.join(output, subs['sid'] + '_' + COORD_TMPL.format(desc, content, 'json')),
                            shape=[labels.shape[0], cols], desc='Time steps of the simulated time series.',
                            key='coord')


def read_csv(path, sep):
    try:
        f = pd.read_csv(path, sep=sep, header=None, index_col=False)
    except pd.errors.EmptyDataError:
        return ''
    except ValueError:
        return ''
    else:
        return f
