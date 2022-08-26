import json
import os
from collections import OrderedDict

import pandas as pd

from incf.app import app
from incf.generate import subjects
import incf.templates.templates as temp

# define naming conventions
DEFAULT_TEMPLATE = '{}_desc-{}_{}.{}'
COORD_TEMPLATE = 'desc-{}_{}.{}'

# set to true if centres.txt (nodes and labels) are the same
# for all files. In that case, store only one copy of the files
# in the main 'coord' folder in the same scope as CHANGES.txt
IGNORE_CENTRE = False

# location of coord files (nodes and labels) in the scope of
# converted files. This information is used to supplement JSON
# sidecars, specifically `CoordsRows` and `CoordsColumns`
COORDS = None


def save(sub: dict, folders: list, ses: str = None, name: str = None) -> None:
    """Main engine to save all conversions. Several functionalities to understand:

    1. Check all centres files to see if they have identical content. If so,
       only one copy gets saved in the main area of the output folder (by default
       this folder is in root level of the project in 'output' folder), specifically,
       in 'coord' folder. The same structure is applied for single-subject inputs.
       The final structure will have the following layout:
                            |__ output
                                |__ coord
                                    |__ desc-<label>_<suffix>.json
                                    |__ desc-<label>_<suffix>.tsv

       Otherwise, if input data has multi-subject files, the 'coord' folder will be
       deleted in the root-level. The final structure will have the following layout:
                            |__ output
                                |__ sub-<ID>
                                    |__ coord
                                        |__ sub-<ID>_desc-<label>_<suffix>.json
                                        |__ sub-<ID>_desc-<label>_<suffix>.tsv

       To overcome redundancy, the first run will happen as usual; it will check all
       centres files and update the global parameter IGNORE_CENTRE. This argument indicates
       whether the following centres should be omitted or not. If true, the function will
       immediately break. Otherwise, all centres will be stored in their respective folders.

    2. Read file contents. This is pretty straight-forward, given a file location,
       the app gets its contents. Supported file types are '.txt', '.csv', '.dat', '.mat',
       and '.h5'.

       Tips:
            1. Make sure to have 1 (!) array in MATLAB (.mat), HDF5 (.h5) files. If there
               are multiple arrays, the app will ignore them.
            2. Make sure to store textual data (e.g., 'lh_bankssts') in the first column (!)
               of 'centres.txt' file. When 'centres.txt' file is passed, the app divides its
               columns to labels (Nx1, 1st column) and nodes (NxN-1, 2nd-Nth column). If you
               have nodes and labels separated in 'nodes.txt' and 'labels.txt' files, you
               can safely ignore this information.

    3. Get folder locations. Depending on the passed file, get its respective folder location.

    4. Save files.

    Parameters
    ----------
    sub :
        param folders:
    ses :
        param name:
    sub: dict :

    folders: list :

    ses: str :
         (Default value = None)
    name: str :
         (Default value = None)

    Returns
    -------

    """
    global IGNORE_CENTRE

    # check if centres should be ignored. If so, immediately break
    # the function. Otherwise, continue iteration.
    if IGNORE_CENTRE and name == 'centres':
        return

    # read file contents
    file = open_file(sub['path'], sub['sep'])

    # get folder location for weights and distances
    if name == 'wd':
        # set appropriate output path depending on session type
        if ses is None:
            folder = folders[1]
        else:
            folder = folders[2]

        # get description for weights or distances
        desc = temp.weights if 'weights' in sub['name'] else temp.distances

        # save conversion results
        save_files(sub, folder, file, desc=desc, ftype='wd')

    # get folder location for centres
    if name == 'centres':
        # check if all centres are of the same content
        if check_centres():
            # ignore preceding centres files
            IGNORE_CENTRE = True

            # set output path to store coords in
            folder = os.path.join(app.OUTPUT, 'coord')

            # save conversion results
            save_files(sub, folder, file, type='coord', centres=True, desc=temp.centres['multi-same'])
        else:
            # get description for centres depending on input files
            desc = temp.centres['multi-unique'] if app.MULTI_INPUT else temp.centres['single']

            # set appropriate output path depending on session and subject types
            if ses is not None:
                folder = folders[4]
            elif app.MULTI_INPUT and ses is None:
                folder = folders[3]
            else:
                folder = os.path.join(app.OUTPUT, 'coord')

            # save conversion results
            save_files(sub, folder, file, type='default', centres=True, desc=desc)


def save_files(sub, folder, content, type='default', centres=False, desc=None, ftype='centres'):
    """

    Parameters
    ----------
    sub :
        param folder:
    content :
        param type:
    centres :
        param desc: (Default value = False)
    ftype :
        return: (Default value = 'centres')
    folder :

    type :
         (Default value = 'default')
    desc :
         (Default value = None)

    Returns
    -------

    """
    global COORDS

    if type == 'default':
        json_file = os.path.join(folder, DEFAULT_TEMPLATE.format(sub['sid'], sub['desc'], sub['name'], 'json'))
        tsv_file = json_file.replace('json', 'tsv')
    else:
        json_file = os.path.join(folder, COORD_TEMPLATE.format(sub['desc'], sub['name'], 'json'))
        tsv_file = json_file.replace('json', 'tsv')

    # Save 'centres.txt' as 'nodes.txt' and 'labels.txt'. This will require breaking the
    # 'centres.txt' file, the first column HAS TO BE labels, and the rest N dimensions
    # are nodes.
    if centres:
        # create names for nodes and labels
        # Since the usual structure leaves the name of the files as is,
        # we need to make sure we save 'nodes' and 'labels' appropriately.
        # If we didn't create these two values below, both labels and nodes
        # would be stored as 'sub-<ID>_desc-<label>_centres.txt', and the
        # content would only have nodes.
        labels = json_file.replace(sub['name'], 'labels')
        nodes = json_file.replace(sub['name'], 'nodes')

        if COORDS is None:
            COORDS = [labels, nodes]

        # save labels to json and tsv
        to_json(labels, shape=[content.shape[0], 1], key='coord', desc=desc[0])
        to_tsv(labels.replace('json', 'tsv'), content[0])

        # save nodes to json and tsv
        to_json(nodes, shape=content.shape, key='coord', desc=desc[1])
        to_tsv(nodes.replace('json', 'tsv'), content[1:])
    else:
        # otherwise, save files as usual
        to_json(json_file, shape=content.shape, key=ftype, desc=desc)
        to_tsv(tsv_file, content)


def check_centres():
    """


    """
    # get all centres files
    centres = get_specific('centres')
    file = open_file(centres[0], subjects.find_separator(centres[0]))

    same = {}

    # iterate over centres
    for centre in centres[1:]:
        same.update(file == open_file(centre, subjects.find_separator(centre)))

    if len(same) == 1:
        if bool(same):
            return True
        return False
    return False


def get_specific(filetype: str) -> list:
    """Get all files that correspond to the filetype. For example,
    if filetype is equal to "areas", this function will return
    all files containing that keyword.

    Parameters
    ----------
    filetype :
        return:
    filetype: str :


    Returns
    -------

    """

    content = []

    for file in app.ALL_FILES:
        if filetype in file:
            content.append(file)

    return content


def open_file(path: str, sep: str):
    """

    Parameters
    ----------
    path :
        param sep:
    path: str :

    sep: str :


    Returns
    -------

    """

    ext = path.split('.')[-1]

    if ext in ['txt', 'csv', 'dat']:
        return open_text(path, sep)

    elif ext == 'mat':
        pass

    elif ext == 'h5':
        pass


def open_text(path, sep):
    """

    Parameters
    ----------
    path :
        param sep:
    sep :


    Returns
    -------

    """
    try:
        f = pd.read_csv(path, sep=sep, header=None, index_col=False)
    except pd.errors.EmptyDataError:
        return ''
    except ValueError:
        return ''
    else:
        return f


def to_tsv(path, file, sep=None):
    """

    Parameters
    ----------
    path :
        param file:
    sep :
        return: (Default value = None)
    file :


    Returns
    -------

    """
    params = {'sep': '\t', 'header': None, 'index': None}
    sep = sep if sep != '\n' else '\0'

    if isinstance(file, str) and sep is not None:
        pd.read_csv(file, index_col=None, header=None, sep=sep).to_csv(path, **params)
    else:
        try:
            pd.DataFrame(file).to_csv(path, **params)
        except ValueError:
            with open(file) as f:
                with open(path, 'w') as f2:
                    f2.write(f.read())


def to_json(path, shape, desc, key, **kwargs):
    """

    Parameters
    ----------
    path :
        param shape:
    desc :
        param key:
    kwargs :
        return:
    shape :

    key :

    **kwargs :


    Returns
    -------

    """
    inp = temp.required
    out = OrderedDict({x: '' for x in inp})

    if key != 'wd':
        struct = temp.struct[key]
        out.update({x: '' for x in struct['required']})
        out.update({x: '' for x in struct['recommend']})

    with open(path, 'w') as file:
        json.dump(temp.populate_dict(out, shape=shape, desc=desc, coords=COORDS, **kwargs), file)
