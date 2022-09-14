import json
import os
from collections import OrderedDict

import pandas as pd

from sim2bids.app import app
from sim2bids.generate import subjects
import sim2bids.templates.templates as temp

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

NETWORK = []


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
    sub (dict):
        Dictionary containing information of one file only. For example,
        {'name': 'centres', 'fname': 'centres.txt', 'sid': 'sub-01', 'desc': 'default',
        'sep': '\t', 'path': PATH_TO_FILE, 'ext': 'txt'}
    folders (list):
        List of folders corresponding to whether input files have single- or
        multi-subject, or session-based structure. Each structure contains a
        different sequence of folders created in 'app.py' in 'create_sub_struct' function.
    ses (str):
        Session type (ses-preop, ses-postop, None). If sessions are present,
        appropriate files are stored in their appropriate session folders.
        Otherwise, the structure follows the standard layout.
    name (str):
        Name of the file. Accepted names:
            'weight', 'distance', 'tract_length', 'delay', 'speed',                 # Network (net)
            'nodes', 'labels', 'centres', 'area', 'hemisphere', 'cortical',         # Coordinates (coord)
            'orientation', 'average_orientation', 'normal', 'times', 'vertices',    # Coordinates (coord)
            'faces', 'vnormal', 'fnormal', 'sensor', 'map', 'volume',               # Coordinates (coord)
            'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d',                     # Coordinates (coord)
            'vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event', 'emp'     # Timeseries (ts)
            'fc'                                                                    # Spatial (spatial)
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
        desc = temp.file_desc['weights'] if 'weights' in sub['name'] else temp.file_desc['distances']

        if 'content' in sub.keys():
            save_files(sub, folder, sub['content'], ftype='wd')
        else:
            # save conversion results
            save_files(sub, folder, file, desc=desc, ftype='wd')

    # get folder location for centres
    elif name == 'centres':
        save_centres(sub, file, ses, folders)

    # get folder location for spatial
    elif name in ['spatial', 'fc']:
        desc = temp.file_desc['spatial']

        if ses is None:
            folder = folders[2]
        else:
            folder = folders[3]

        if 'content' in sub.keys():
            save_files(sub, folder, sub['content'], type='default', ftype='spatial', desc=desc)
        else:
            # save conversion results
            save_files(sub, folder, file, type='default', ftype='spatial', desc=desc)

    # get folder location for time series
    elif name in ['ts', 'bold']:
        desc = temp.file_desc['ts'] if name == 'ts' else temp.file_desc['bold'].format(sub['sid'].replace('sub-', ''))
        save_files(sub, folders[-1], file, type='default', ftype='ts', desc=desc)

    # get folder location for coordinates
    elif name == 'coord':
        # check nodes
        if 'nodes' in sub['name'] and not IGNORE_CENTRE:
            if 'content' in sub.keys():
                save_centres(sub, sub['content'], ses, folders, centre_name='nodes')
            else:
                save_centres(sub, file, ses, folders, centre_name='nodes')
        else:
            # set appropriate output path depending on session and subject types
            if ses is not None:
                folder = folders[4]
            elif app.MULTI_INPUT and ses is None:
                folder = folders[3]
            else:
                folder = os.path.join(app.OUTPUT, 'coord')

            if 'content' in sub.keys():
                save_files(sub, folder, file, type='default', centres=True)
            else:
                # save conversion results
                if 'centres' in sub['fname']:
                    if IGNORE_CENTRE or not app.MULTI_INPUT:
                        save_files(sub, folder, file, type='other', centres=True, desc=temp.centres['single'])
                    else:
                        save_files(sub, folder, file, type='default', centres=True, desc=temp.centres['multi-unique'])
                else:
                    if IGNORE_CENTRE or not app.MULTI_INPUT:
                        save_files(sub, folder, file, type='other', desc=temp.file_desc[sub['name']])
                    else:
                        save_files(sub, folder, file, type='default', desc=temp.file_desc[sub['name']])


def save_centres(sub, file, ses, folders, centre_name='centres'):
    global IGNORE_CENTRE

    # check if all centres are of the same content
    if check_centres(name=centre_name):
        # ignore preceding centres files
        IGNORE_CENTRE = True

        # set output path to store coords in
        folder = os.path.join(app.OUTPUT, 'coord')

        # save conversion results
        save_files(sub, folder, file, type='other', centres=True, desc=temp.centres['multi-same'])
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
        if IGNORE_CENTRE:
            save_files(sub, folder, file, type='other', centres=True, desc=desc)
        else:
            save_files(sub, folder, file, type='default', centres=True, desc=desc)


def save_h5(sub, folders, ses=None):
    pass


def save_files(sub: dict, folder: str, content, type: str = 'default', centres: bool = False,
               desc: [str, list, None] = None, ftype: str = 'coord'):
    """
    This function prepares the data to be stored in JSON/TSV formats. It first creates
    absolute paths where data is to be stored, deals with 'centres.txt' file and
    preprocesses it. Then, sends the finalized versions to the function that
    saves JSON and TSV files.

    Parameters
    ----------
    sub (dict):
        Dictionary containing information of one file only. For example,
        {'name': 'centres', 'fname': 'centres.txt', 'sid': 'sub-01', 'desc': 'default',
        'sep': '\t', 'path': PATH_TO_FILE, 'ext': 'txt'}
    folder (str):
        Folder where to store output conversions for the specific file. For example,
        if the passed file is 'weights.txt' and the input files have both sessions and
        multi-subject structure, then 'weights.txt' will be stored like:
                            |__ output
                                |__ sub-<ID>
                                    |__ ses-preop
                                        |__ net
                                            |__ sub-<ID>_desc-<label>_weights.json
                                            |__ sub-<ID>_desc-<label>_weights.tsv
    content (pd.DataFrame, np.array, ...)
        Content of the specific file.
    type (str):
        Type of default name to use. There are two options: default and coordinate.
        The first creates the following file name:
                                sub-<ID>_desc-<label>_<suffix>.json|.tsv
        The other creates the following file name (basically, omitting the ID):
                                    desc-<label>_<suffix>.json|.tsv
    centres (bool):
        Whether the file is 'centres.txt'. Centres require additional treatment as
        splitting the folder into 'nodes.txt' and 'labels.txt', therefore, it should
        be distinguished from others.
    desc (str):
        Description of the file; this information will be added to the JSON sidecar.
    ftype (str):
        File type of the passed file. Accepted types:
            'wd' (weights and distances), 'coord' (coordinate), 'ts' (time series),
            'spatial', 'eq' (equations), 'param' (parameters), and 'code'.
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
            if IGNORE_CENTRE or not app.MULTI_INPUT:
                COORDS = [f'../coord/desc-{app.DESC}_labels.json', f'../coord/desc-{app.DESC}_nodes.json']
            else:
                COORDS = [labels.replace(app.OUTPUT, '../..').replace('\\', '/'),
                          nodes.replace(app.OUTPUT, '../..').replace('\\', '/')]

        # save labels to json and tsv
        to_json(labels, shape=[content.shape[0], 1], key='coord', desc=desc[0])
        to_tsv(labels.replace('json', 'tsv'), content.iloc[:, 0])

        # save nodes to json and tsv
        to_json(nodes, shape=[content.shape[0], content.shape[1] - 1], key='coord', desc=desc[1])
        to_tsv(nodes.replace('json', 'tsv'), content.iloc[:, 1:])
    else:
        if ftype == 'coord':
            if sub['name'] == 'bold_times':
                desc = temp.file_desc['bold_times'].format(sub['sid'])
            to_json(json_file.lower(), shape=content.shape, key='coord', desc=desc)
            to_tsv(tsv_file.lower(), content)
        else:
            # otherwise, save files as usual
            to_json(json_file.lower(), shape=content.shape, key=ftype, desc=desc)
            to_tsv(tsv_file.lower(), content)


def check_centres(name='centres'):
    """
    This function checks all centres files in the input folder and
    decides whether they have the same content or not. The logic of
    this functionality is the following, we take the first arbitrary
    centres.txt file and compare it to the rest. We don't check every
    single centres file against the rest. Thus, only one checking round
    happens here.

    It's important to note that if users pass in 2+ subject folders and only
    one contains centres.txt, the 'coord' folder is created for one subject only.
    """

    # get all centres files
    centres = get_specific(name)

    # get the first element
    file = open_file(centres[0], subjects.find_separator(centres[0]))

    # define set literal
    same = {}

    # iterate over centres
    for centre in centres[1:]:
        # append to the set literal whether the contents of the first element
        # are the same with the rest
        same.update(file == open_file(centre, subjects.find_separator(centre)))

    # check if set literal contains only one element
    if len(same) == 1:
        if bool(same):
            # if files are the same, return True
            return True
        # False otherwise
        return False
    return False


def get_specific(filetype: str) -> list:
    """
    Get all files that correspond to the filetype. For example,
    if filetype is equal to "areas", this function will return
    all files containing that keyword.

    Parameters
    ----------
    filetype: str
        Type of the file to search for. Accepted types:
            'weight', 'distance', 'tract_length', 'delay', 'speed',                 # Network (net)
            'nodes', 'labels', 'centres', 'area', 'hemisphere', 'cortical',         # Coordinates (coord)
            'orientation', 'average_orientation', 'normal', 'times', 'vertices',    # Coordinates (coord)
            'faces', 'vnormal', 'fnormal', 'sensor', 'map', 'volume',               # Coordinates (coord)
            'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d',                     # Coordinates (coord)
            'vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event', 'emp'     # Timeseries (ts)
            'fc'                                                                    # Spatial (spatial)

    Returns
    -------
        Returns a list of all files that end with the specified filetype.
    """

    # create emtpy list to store appropriate files
    content = []

    # iterate over all files found by the app previously
    for file in app.ALL_FILES:
        # check if the keyword is present
        if filetype in file:
            # if yes, append the value
            content.append(file)

    # return the list of newly-found files
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
    if sep == '\n':
        return pd.read_csv(path, header=None, index_col=None)

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

    params = {'ModelEq': f'../eq/desc-{app.DESC}_eq.xml',
              'ModelParam': f'../param/desc-{app.DESC}_param.xml',
              'SourceCode': f'../code/desc-{app.DESC}_code.py',
              'SoftwareVersion': app.SoftwareVersion,
              'SoftwareRepository': app.SoftwareRepository,
              'SourceCodeVersion': app.SoftwareVersion,
              'SoftwareName': app.SoftwareName,
              'Network': NETWORK
              }

    if key != 'wd':
        struct = temp.struct[key]
        out.update({x: '' for x in struct['required']})

    for k in ['ModelEq', 'ModelParam', 'SourceCode', 'SoftwareVersion', 'SourceCodeVersion',
              'SoftwareRepository', 'SoftwareName', 'Network']:
        if k in out.keys():
            out[k] = params[k]

    if 'Units' in out.keys() and key != 'coord':
        out['Units'] = 'ms'

    # point coord files to nodes/labels TSV files instead
    coord = COORDS if key != 'coord' else [COORDS[0].replace('json', 'tsv'), COORDS[1].replace('json', 'tsv')] \
        if COORDS is not None else COORDS

    with open(path, 'w') as file:
        json.dump(temp.populate_dict(out, shape=shape, desc=desc, coords=coord, **kwargs), file)
