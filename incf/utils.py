import os
import shutil

import panel as pn
import incf.templates.templates as temp
import incf.app as app


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
                                'fnormals', 'sensors', 'conv', 'map', 'volumes',
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
    app.REQUIRED = []

    widget = pn.WidgetBox()

    for k, v in json_editor.items():
        specs = temp.struct
        reqs = temp.required
        root = os.path.basename(os.path.dirname(selected))
        req = k in specs[root]['required']

        if k in reqs or req:
            app.REQUIRED.append(k)
            name = f'Specify {k} (REQUIRED):'
        else:
            name = f'Specify {k} (RECOMMENDED):'

        if k == 'Units' and v == '' and name is not None:
            widget.append(pn.widgets.Select(name=name, options=app.UNITS, value=''))
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
        if name in app.REQUIRED and widget.value == '':
            return False
    return True
