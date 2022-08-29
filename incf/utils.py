import os
import shutil

import panel as pn

import incf.app as app
import incf.generate.subjects as subj
import incf.preprocess.preprocess as prep
import incf.templates.templates as temp
from incf import incf
from incf.convert import convert


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

    print('Removed all test files...')


def get_selector(name):
    return pn.widgets.Select(name=f'Specify {name}', groups={
        'Network (net)': ['weights', 'distances', 'delays', 'speed', 'weights & nodes'],
        'Coordinates (coord)': ['times', 'centres', 'orientations', 'areas', 'hemispheres',
                                'cortical', 'nodes', 'labels', 'vertices', 'faces', 'vnormals',
                                'fnormals', 'sensors', 'app', 'map', 'volumes',
                                'cartesian2d', 'cartesian3d', 'polar2d', 'polar3d'],
        'Timeseries (ts)': ['ts', 'emp', 'vars', 'stimuli', 'noise', 'spikes', 'raster', 'events'],
        'Spatial (spatial)': ['fc', 'map'],
        'Code (code)': ['code'],
        'Skip file type': ['skip']
    })


def append_widgets(files):
    widgets = ['### Preprocessing step: rename files']

    for file in files:
        widgets.append(get_selector(file))

    return widgets


def get_settings(json_editor, selected):
    incf.REQUIRED = []

    widget = pn.WidgetBox()

    for k, v in json_editor.items():
        specs = temp.struct
        reqs = temp.required
        root = os.path.basename(os.path.dirname(selected))
        req = k in specs[root]['required']

        if k in reqs or req:
            incf.REQUIRED.append(k)
            name = f'Specify {k} (REQUIRED):'
        else:
            name = f'Specify {k} (RECOMMENDED):'

        if k == 'Units' and v == '' and name is not None:
            widget.append(pn.widgets.Select(name=name, options=incf.UNITS, value=''))
        elif k not in ['NumberOfColumns', 'NumberOfRows', 'Units']:
            if len(v) > 0 and k in ['CoordsColumns', 'CoordsRows']:
                continue
            if v == '' and name is not None:
                widget.append(pn.widgets.TextInput(name=name))

    # append button
    return widget


def verify_complete(widgets):
    for widget in widgets:
        name = widget.name.split(' ')[-2]
        if name in incf.REQUIRED and widget.value == '':
            return False
    return True
