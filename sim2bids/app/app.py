import json
import os
import re
import shutil
from collections import OrderedDict
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
import panel as pn
import pylems_py2xml
import lems.api as lems

# import local packages
import requests

import sim2bids.utils
from sim2bids.generate import structure, subjects
from sim2bids.preprocess import preprocess as prep
from sim2bids.convert import convert, mat
from sim2bids.templates import templates as temp
from sim2bids.app import utils
from sim2bids.generate import models, global_files

# =========================================
#        CUSTOMIZABLE WITH USER INPUT
# =========================================

OUTPUT = 'output'  # output folder to store conversions
DESC = 'default'  # short description that identifies input data
INPUT = 'inputs'  # placeholder to store preprocessed input files

# model specific inputs
MODEL_NAME = None
MODEL_PARAMS = None
RHYTHMS = None
SoftwareVersion = None
SoftwareRepository = None
SoftwareName = None
SoftwareCode = 'MISSING'
COND_SPEED = 'cspeed'
GLB_COUP_SF = 'csf'

# =========================================
#        DO NOT CHANGE THESE VALUES
# =========================================

# define global variables
SID = None
INPUT_TRANSFERRED = False
CENTRES = False  # whether centres.txt|nodes.txt|labels.txt were found
MULTI_INPUT = False  # whether input files include single- or multi-subjects
ALL_FILES = None  # list of all file paths (gets supplemented in subjects.py)
CODE = None  # path to python code if exists
SESSIONS = False
H5_CONTENT = dict()
MISSING = []

# store different time series accounting for 'times'
TIMES = []

# define all accepted files
ACCEPTED = ['weight', 'distance', 'tract_length', 'delay', 'speeds',                     # Network (net)
            'nodes', 'labels', 'centre', 'area', 'hemisphere', 'cortical',               # Coordinates (coord)
            'orientation', 'average_orientation', 'normals', 'times', 'bold_ts', 'vertices',        # Coordinates (coord)
            'faces', 'vnormal', 'fnormal', 'sensor', 'volume', 'map',                   # Coordinates (coord)
            'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d',                         # Coordinates (coord)
            'vars', 'stimuli', 'noise', 'spike', 'raster', 'ts', 'event',               # Timeseries (ts)
            'emp', 'bold_times', 'hrf'                                             # Timeseries (ts)
            'emp_fc', 'fc']                                                                       # Spatial (spatial)

TO_EXTRACT = ['weights.txt', 'centres.txt', 'distances.txt',  # folder "net"
              'areas.txt', 'average_orientations.txt', 'cortical.txt',  # folder "coord"
              'hemisphere.txt', 'normals.txt']  # folder "coord"

# define accepted extensions
ACCEPTED_EXT = ['txt', 'csv', 'dat', 'h5', 'mat', 'zip', 'py', 'npy']


def main(path: str, files: list, subs: dict = None, save: bool = False, layout: bool = False):
    """Main brain function that creates subjects, auto-generated structure,
    and saves apperted files.

    Parameters
    ----------
    path :
        param files:
    subs :
        param save:
    layout :
        return:
    path: str :

    files: list :

    subs: dict :
         (Default value = None)
    save: bool :
         (Default value = False)
    layout: bool :
         (Default value = False)

    Returns
    -------
    :param input_path:

    """
    global MODEL_NAME, INPUT, INPUT_TRANSFERRED

    # whether to generate layout
    if layout:
        # if no subjects are passed, define them
        if subs is None:
            subs = subjects.Files(path, files).subs
            results = convert.check_centres()
            if results:
                convert.IGNORE_CENTRE = results

    # only save conversions if 'save' is True
    if save and subs:
        save_output(subs)

        if utils.RHYTHMS:
            save_params()

        if MISSING:
            save_missing(path, MISSING)

        # save code
        if CODE:
            utils.infer_model()
            save_code()

        global_files.add_global_files()
        check_output()
        pn.state.notifications.success(f'{OUTPUT} folder is ready!')

    if H5_CONTENT is not None and 'model' in H5_CONTENT.keys():
        pylems_py2xml.main.XML(inp=H5_CONTENT, output_path=os.path.join(OUTPUT, 'param'),
                               uid=H5_CONTENT['model'], app=True, suffix=DESC)
        MODEL_NAME = utils.get_model()
        transfer_xml()

    # finally, remove all empty folders
    remove_empty()

    # return subjects and possible layouts only if it's enabled
    if layout:
        return subs, structure.create_layout(subs)

    # otherwise, return None
    return None


def preprocess_input(path, input_files):
    to_preprocess = {}

    for root, dirs, files in os.walk(path):
        for file in files:
            if file in input_files:
                continue

            if file.endswith('mat') and 'csf' not in root and 'cspeed' not in root and root != path:
                if root not in to_preprocess:
                    to_preprocess[root] = []
                to_preprocess[root].append(file)

    for root, content in to_preprocess.items():
        for c in content:
            cspeed = re.findall(r'speed_[0-9]+', c)

            if cspeed:
                cspeed = cspeed[0].replace('speed_', '')
                csf = re.findall(r'csf_[0-9\.]+', c)[0].replace('csf_', '')

                path = os.path.join(root, f'{COND_SPEED}{cspeed}')
                if not os.path.exists(path):
                    os.mkdir(path)

                path = os.path.join(path, f'csf {csf}')
                if not os.path.exists(path):
                    os.mkdir(path)

                # copy file
                shutil.move(os.path.join(root, c), path)


def save_params():
    global MODEL_NAME

    # verify path exists
    path = os.path.join(OUTPUT, 'param')
    if not os.path.exists(path):
        os.mkdir(path)

    for rhythm, params in utils.RHYTHMS.items():
        if len(params) > 0:
            for param in params:
                model = save_model(param)
                p = os.path.join(path, f'desc-{DESC}_{rhythm}_{param[0]}_G{param[1]}.xml')
                model.export_to_file(p)

                if MODEL_NAME is None and CODE:
                    utils.infer_model()
                if MODEL_NAME is None:
                    MODEL_NAME = ''

                convert.to_json(p.replace('xml', 'json'), shape=None, key='param',
                                desc=f'These are the global parameters for the {MODEL_NAME} model.')


def save_model(param):
    model = lems.Model()
    ct = lems.ComponentType(name='global_parameters')
    ct.add(lems.Constant(name='global_speed', value=param[0].replace('speed', '')))
    ct.add(lems.Constant(name='global_coupling', value=param[1]))
    model.add(ct)
    return model


def save_missing(path, files):
    global CODE

    if len(files) == 1 and os.path.isdir(os.path.join(path, files[0])):
        path = os.path.join(path, files[0])

    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)

    get_path = lambda x: Path(os.path.join(path, x))
    missing = [get_path(p) for p in os.listdir(path) if not os.path.isdir(get_path(p))]

    for file in missing:
        name = os.path.basename(str(file)).split('.')[0]
        file = str(file)

        if file.endswith('.py'):
            CODE = file
        elif 'centre' in file:

            if not os.path.exists(os.path.join(OUTPUT, 'coord')):
                os.mkdir(os.path.join(OUTPUT, 'coord'))

            f = convert.open_file(os.path.join(path, file), subjects.find_separator(os.path.join(path, file)))
            convert.save_files(dict(desc=DESC, name=name), f'{OUTPUT}/coord', f,
                               type='coord', centres=True, desc=temp.centres['single'])

        elif 'participants' in file or 'CHANGES' in file or 'description' in file or 'README' in file:
            if not os.path.exists(os.path.join(OUTPUT, os.path.basename(file).replace('.txt', '') + '.txt')):
                shutil.copy(file, OUTPUT)


def save_output(subs):
    """

    Parameters
    ----------
    subs :
        return:

    Returns
    -------

    """

    # create the folder that will store conversions
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)

    # prepare the output folder
    check_output_folder()

    # verify folders exist
    structure.check_folders(OUTPUT)

    def save(sub, ses=None):
        """

        Parameters
        ----------
        sub :

        ses :
             (Default value = None)

        Returns
        -------

        """
        name = None

        for k, v in sub.items():

            # create folders according to session and subject count types
            folders = create_sub_struct(OUTPUT, v, ses_name=ses)
            k_lower = k.lower()

            if 'weight' in k_lower or 'distance' in k_lower:
                name = 'wd'
            elif 'centres' == k_lower:
                name = 'centres'
            elif 'fc' in k_lower or 'emp_fc' in k_lower or 'map' in k_lower:
                name = 'spatial'
            elif 'times' in k_lower:
                name = 'times'
            elif 'vars' in k_lower or 'stimuli' in k_lower or 'noise' in k_lower \
                    or 'spike' in k_lower or 'raster' in k_lower or 'ts' in k_lower \
                    or 'event' in k_lower or 'emp' in k_lower or 'bold' in k_lower or 'hrf' in k_lower:
                name = 'ts'
            elif k_lower.endswith('.h5'):
                convert.save_h5(sub[k], folders, ses=None)
                continue
            elif k_lower.endswith('.mat'):
                mat.save_mat(sub[k], sub[k]['path'], extract=False)
            elif subjects.accepted(k_lower):
                name = 'coord'

            if name is not None:
                convert.save(sub[k], folders, ses=ses, name=name)

    # iterate over files and save them
    for k, v in subs.items():
        if 'ses-preop' in v.keys() or 'ses-postop' in v.keys():
            for k2, v2 in v.items():
                save(v2, ses=k2)
        else:
            save(v)


def check_output_folder():
    """ """
    # check if the output folder already contains files,
    # if true, notify about removal and remove folder with its contents
    conflict = len(os.listdir(OUTPUT)) > 0

    if conflict:
        pn.state.notifications.info('Output folder contains files. Removing them...')
        sim2bids.utils.rm_tree(OUTPUT)
        prep.reset_index()


def create_sub_struct(path, subs=None, ses_name=None):
    """

    Parameters
    ----------
    path :

    subs :

    ses_name :
         (Default value = None)

    Returns
    -------

    """
    if ses_name in ['ses-preop', 'ses-postop']:
        sub = os.path.join(path, subs['sid'])
        ses = os.path.join(sub, ses_name)
        net_ses = os.path.join(ses, 'net')
        spatial_ses = os.path.join(ses, 'spatial')
        coord_ses = os.path.join(ses, 'coord')
        ts_ses = os.path.join(ses, 'ts')
        folders = [sub, ses, net_ses, spatial_ses, coord_ses, ts_ses]
    else:
        sub = os.path.join(path, subs['sid'])
        net = os.path.join(sub, 'net')
        spatial = os.path.join(sub, 'spatial')
        ts = os.path.join(sub, 'ts')

        if MULTI_INPUT:
            coord = os.path.join(sub, 'coord')
            folders = [sub, net, spatial, coord, ts]
        else:
            folders = [sub, net, spatial, ts]

    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)

    return folders


def save_code():
    """

    Parameters
    ----------
    subs :


    Returns
    -------

    """

    utils.infer_model()

    path = 'https://github.com/the-virtual-brain/tvb-root/archive/refs/tags/{}.zip'

    if SoftwareName == 'TVB':
        if SoftwareVersion == 1.5:
            path = path.replace(SoftwareVersion, '1.5.10')
        elif SoftwareVersion:
            path = path.format(str(SoftwareVersion))

        req = requests.get(path)

        if req.status_code == 200:
            path = os.path.join(OUTPUT, 'code', f'tvb-framework-{SoftwareVersion}.zip')
            with open(path, 'wb') as output:
                output.write(req.content)
            with ZipFile(path, 'r') as file:
                file.extractall(path=os.path.join(OUTPUT, 'code'))

            os.remove(path)
            path = os.path.join(OUTPUT, 'code', f'tvb-root-{SoftwareVersion}')
            os.rename(path, path.replace('root', 'framework'))

        else:
            pn.state.notifications.error('Please check the TVB version!', duration=5000)

    if isinstance(CODE, str) and CODE.endswith('.py'):
        template = f'code.py'
        path = os.path.join(OUTPUT, 'code', template)

        shutil.copy(CODE, path)
        supply_dict('code', os.path.join(path.replace('py', 'json')))

        if MODEL_PARAMS:
            models.set_params(DESC, rhythm=None, **MODEL_PARAMS)
        else:
            models.set_params(DESC, rhythm=None)

    elif isinstance(CODE, list):
        for code in CODE:
            name = os.path.basename(code)
            ext = name.split('.')[-1]
            desc = f'desc-{name.replace(ext, "").replace(".", "")}_code.{ext}'

            # copy file
            shutil.copy(code, os.path.join(OUTPUT, 'code', desc))
            convert.to_json(os.path.join(OUTPUT, 'code', desc.replace(ext, 'json')), None,
                            temp.file_desc['code'], 'code')

            models.set_params(DESC, None, **MODEL_PARAMS)


def transfer_xml():
    # transfer results to appropriate folders
    path = os.path.join(OUTPUT, 'param', '_eq.xml')
    if os.path.exists(path):
        shutil.move(path, os.path.join(OUTPUT, 'eq'))

    # add json sidecars
    supply_dict('eq', os.path.join(OUTPUT, 'eq', '_eq.json'))
    supply_dict('param', os.path.join(OUTPUT, 'param', 'param.json'))

    # remove model
    path = os.path.join(OUTPUT, 'param', f'model-{MODEL_NAME}_param.xml')

    if os.path.exists(path):
        os.remove(path)


def supply_dict(ftype, path):
    file = OrderedDict()

    def get_dict(reqs):
        return {x: '' for x in temp.struct[ftype][reqs]}

    def save():
        with open(path, 'w') as f:
            json.dump(file, f)

    if len(temp.struct[ftype]['required']) > 0:
        file.update(get_dict('required'))

    eq = '../eq/eq.xml'
    file['SourceCode'] = f'../code/code.py'

    for key, val in zip(['SoftwareVersion', 'SoftwareRepository', 'SoftwareName'],
                        [SoftwareVersion, SoftwareRepository, SoftwareName]):
        if val is not None:
            if key == 'SoftwareVersion':
                file['SourceCodeVersion'] = val

            file[key] = val

    if ftype == 'code':
        file['ModelEq'] = eq
        file['Description'] = 'The source code to reproduce results.'
    elif ftype == 'param':
        file['ModelEq'] = eq
        file['Description'] = f'These are the parameters for the {MODEL_NAME} model.'
    elif ftype == 'eq':
        file['Description'] = f'These are the equations to simulate the time series with the {MODEL_NAME} model.'

    save()


def remove_empty():
    """Recursively traverse generated output folder and remove all empty folders."""

    # get contents of the specified path
    for root, dirs, files in os.walk(OUTPUT):
        # if folder is empty, remove it
        if len(os.listdir(root)) == 0:
            os.removedirs(root)


def duplicate_folder(path):
    """

    Parameters
    ----------
    path :


    Returns
    -------

    """

    # create folder if it doesn't exist
    root = os.path.join('..', 'data')
    new_path = os.path.join(root, os.path.basename(os.path.dirname(path + '\\')))

    if not os.path.exists(root):
        os.mkdir(root)

    if not os.path.exists(new_path):
        shutil.copytree(path, new_path, symlinks=False, ignore=None, ignore_dangling_symlinks=False,
                        dirs_exist_ok=False)
    # set PATH to a new path
    return new_path


def check_output():
    for directory in ['code', 'coord', 'eq', 'param']:
        path = os.path.join(OUTPUT, directory)

        if os.path.exists(path) and len(os.listdir(path)) > 0:
            for file in os.listdir(path):
                if file.startswith('sub-'):
                    match = re.match('sub-[0-9]+', file)[0]
                    os.replace(os.path.join(path, file), os.path.join(path, file.replace(match, '').strip('_')))

