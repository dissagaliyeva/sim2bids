import os
import shutil

import panel as pn

import sim2bids.app as app
import sim2bids.generate.subjects as subj
import sim2bids.preprocess.preprocess as prep
import sim2bids.templates.templates as temp
from sim2bids import sim2bids
from sim2bids.convert import convert
from sim2bids.generate import subjects


def get_all_files(new_files, old_files, path):
    all_files = new_files

    # for file in old_files:
    #
    #
    #
    #     if subjects.accepted(file):
    #         all_files.append(os.path.join(path, file))

    return all_files

def reset_values():
    prep.reset_index()
    subj.TO_RENAME = None
    app.ALL_FILES = None
    app.MULTI_INPUT = False
    app.CODE = None
    app.CENTRES = False
    app.SID = None
    convert.IGNORE_CENTRE = False
    convert.COORDS = None


def rm_tree(path: str = '../output'):
    assert os.path.exists(path), f'Path `{path}` does not exist'

    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)

    print('Removed all files...')


def get_selector(name):
    return pn.widgets.Select(name=f'Specify {name}', value='skip', groups={
        'Network (net)': ['weights', 'distances', 'delays', 'speed', 'weights & nodes'],
        'Coordinates (coord)': ['times', 'bold_times', 'centres', 'orientations', 'areas', 'hemispheres',
                                'cortical', 'nodes', 'labels', 'vertices', 'faces', 'vnormals',
                                'fnormals', 'sensors', 'app', 'map', 'volumes',
                                'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d'],
        'Timeseries (ts)': ['ts', 'bold_ts', 'emp', 'vars', 'stimuli', 'noise', 'spikes', 'raster', 'events', 'hrf'],
        'Spatial (spatial)': ['fc', 'map', 'emp_fc'],
        'Code (code)': ['code'],
        'Skip file type': ['skip']
    })


def append_widgets(files):
    widgets = ['### Preprocessing step: Rename Files']

    for file in files:
        widgets.append(get_selector(file))

    return widgets


def get_settings(json_editor, selected):
    sim2bids.REQUIRED = []
    to_ignore = ['NumberOfRows', 'NumberOfColumns', 'CoordsRows', 'CoordsColumns', 'ModelEq', 'ModelParam',
                 'SourceCode', 'SoftwareName', 'SoftwareRepository', 'Network']

    widget = pn.WidgetBox()

    root = os.path.basename(os.path.dirname(selected))

    if root == '.ipynb_checkpoints':
        return

    if 'tvb_framework' not in selected and 'tvb-framework':
        reqs, recommend = temp.struct[root]['required'], temp.struct[root]['recommend']

        # iterate over required fields
        for k in reqs:
            if k in json_editor and json_editor[k] == '':
                if k == 'Units':
                    widget.append(pn.widgets.Select(name=f'Specify {k} (REQUIRED):', options=sim2bids.UNITS, value=''))
            else:
                if k not in to_ignore:
                    widget.append(pn.widgets.TextInput(name=f'Specify {k} (REQUIRED):'))
                    # sim2bids.REQUIRED.append(k)

        # iterate over recommended fields
        for k in recommend:
            if k not in to_ignore:
                widget.append(pn.widgets.TextInput(name=f'Specify {k} (RECOMMENDED):'))

        # append button
        return widget


def verify_complete(widgets):
    for widget in widgets:
        name = widget.name.split(' ')[-2]
        if name in sim2bids.REQUIRED and widget.value == '':
            return False
    return True
