import json
import os.path
from collections import OrderedDict

import numpy as np
import pandas as pd

from sim2bids.app import app
from sim2bids.templates import templates as temp


FILE_DESCRIPTIONS = {
    'CHANGES': 'None so far.',
    'README': 'Simulation output{}.',
    'BIDSVersion': 1.7
}

PARTICIPANTS_FIELDS = ['participant_id', 'species', 'age', 'sex', 'handedness', 'strain', 'strain_rrid']


def add_global_files():
    # create CHANGES file if not present
    write_file('CHANGES', FILE_DESCRIPTIONS['CHANGES'])

    # create README file if not present
    if app.MODEL_NAME is not None:
        write_file('README', FILE_DESCRIPTIONS['README'].format(f' for {app.MODEL_NAME} model'))
    else:
        write_file('README', FILE_DESCRIPTIONS['README'].format(''))

    # create dataset_description file if not present
    dataset = OrderedDict()
    dataset['Name'] = app.DESC
    dataset['BIDSVersion'] = FILE_DESCRIPTIONS['BIDSVersion']
    dataset['ReferencesAndLinks'] = []

    if app.SoftwareCode != 'MISSING':
        dataset['ReferencesAndLinks'].append(app.SoftwareCode)
    if app.SoftwareRepository:
        dataset['ReferencesAndLinks'].append(app.SoftwareRepository)
    if app.SoftwareName == 'TVB':
        dataset['ReferencesAndLinks'].append(f'tvb-framework-{app.SoftwareVersion}')

    # save participants file
    write_file('participants.json', dataset, use_json=True)

    # create participants.[tsv|json] file if not present
    check_participants()

    if not os.path.exists(os.path.join(app.OUTPUT, 'participants.tsv')):
        df = pd.DataFrame(columns=['participant_id', 'species', 'age', 'sex', 'handedness', 'strain', 'strain_rrid'],
                          index=None)
        files = os.listdir(app.OUTPUT)

        for file in files:
            if file.startswith('sub-'):
                df = df.append({'participant_id': file}, ignore_index=True)
                df.replace(np.NaN, 'n/a', inplace=True)

        df.to_csv(os.path.join(app.OUTPUT, 'participants.tsv'), index=None, sep='\t')


def write_file(file, content, use_json=False):
    # check if it already exists
    path = os.path.join(app.OUTPUT, file)
    if not os.path.exists(path) and not os.path.exists(path + '.txt'):
        with open(path, 'w') as f:
            if use_json:
                json.dump(content, f)
            else:
                f.write(content)


def get_components(name):
    template = OrderedDict()

    for spec in ['required', 'recommend']:
        template.update({x: '' for x in temp.struct[name][spec]})

    if 'ReferencesAndLinks' in template.keys():
        template['ReferencesAndLinks'] = []

    return template


def check_participants():
    df, path = None, os.path.join(app.OUTPUT, 'participants.tsv')
    json_file = OrderedDict()

    if os.path.exists(path):
        df = pd.read_csv(path, index_col=None, sep='\t')
        columns = [x.lower().strip() for x in df.columns]

        if 'sex' in columns:
            json_file['sex'] = {
                'Description': 'sex of the participant as reported by the participant',
                'Levels': {
                    'M': 'male',
                    'F': 'female'
                }
            }

        if 'handedness' in columns:
            json_file['handedness'] = {
                'Description': 'handedness of the participant as reported by the participant',
                'Levels': {
                    'left': 'left',
                    'right': 'right'
                }
            }

        with open(os.path.join(app.OUTPUT, 'participants.json'), 'w') as f:
            json.dump(json_file, f)


