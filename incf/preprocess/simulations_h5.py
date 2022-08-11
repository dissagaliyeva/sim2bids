import os
import h5py
from incf.convert import convert

COLS = ['weights', 'tract_lengths', 'region_labels', 'centres']
TXT_COLS = ['areas', 'centres', 'cortical', 'hemispheres', 'orientations', 'region_labels', 'tract_lengths', 'weights']


class XML:
    def __init__(self, path, output, save=True):
        self.path = path
        self.params = []
        self.output = output
        self.save = save
        self.file, self.keys, self.eq = None, None, None
        self.template = """<?xml version="1.0" ?>
<Lems xmlns="http://www.neuroml.org/lems/0.7.6" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.neuroml.org/lems/0.7.6 https://raw.githubusercontent.com/LEMS/LEMS/development/Schemas/LEMS/LEMS_v0.7.6.xsd">
    <Component {}/>
</Lems>"""
        self.parse_file()

    def parse_file(self):
        if self.path.endswith('.h5'):
            self.file = h5py.File(self.path)
            self.keys = list(self.file.keys())
            self.eq = list(self.check_keys())

            for k in self.eq:
                self.params.append('{}="{}"'.format(k, self.file[k][:][0]))

            if len(self.params) > 0:
                print(f'Found following parameters:\n{self.params}')
                self.populate_template()

    def check_keys(self):
        return set(self.keys).difference(set(TXT_COLS))

    def populate_template(self):
        if len(self.params) > 0:
            self.template = self.template.format(' '.join(self.params))
            if self.save:
                self.create_xml()

    def create_xml(self):
        with open(self.output, 'w') as f:
            f.write(self.template)


def save(subs, path, folders, ses=None):
    # open h5 file
    data = h5py.File(subs['path'])
    subs['fname'] = subs['fname'].split('_')[0].lower()

    # create subject-specific folders
    if ses is None:
        net = folders[1]
    else:
        net = folders[2]

    # check if `param` values exist
    create_params(check_params(data), [path, net], subs, data)

    # check for `param` folder population
    XML(subs['path'], os.path.join(path, 'param', f'desc-{subs["desc"]}-{subs["fname"]}.xml'))


def check_params(data):
    # check if all the columns are present
    return len(set(COLS).intersection(set(data.keys()))) == 4


def get_paths(paths, subs):
    path, net = paths
    sid, desc, fname = subs['sid'], subs['desc'], subs['fname']

    DEFAULT_TMPL, COORD_TMPL = '{}_desc-{}_{}.{}', 'desc-{}_{}.{}'

    paths = [
        [os.path.join(net, DEFAULT_TMPL.format(sid, desc, 'weights', 'tsv')),
         os.path.join(net, DEFAULT_TMPL.format(sid, desc, 'weights', 'json'))],
        [os.path.join(net, DEFAULT_TMPL.format(sid, desc, 'distances', 'tsv')),
         os.path.join(net, DEFAULT_TMPL.format(sid, desc, 'distances', 'json'))],
        [os.path.join(path, 'coord', COORD_TMPL.format(desc, 'labels', 'tsv')),
         os.path.join(path, 'coord', COORD_TMPL.format(desc, 'labels', 'json'))],
        [os.path.join(path, 'coord', COORD_TMPL.format(desc, 'nodes', 'tsv')),
         os.path.join(path, 'coord', COORD_TMPL.format(desc, 'nodes', 'json'))],
    ]

    return paths, [f'../coords/{fname}_labels.json', f'../coords/{fname}_nodes.json']


def create_params(exists, paths, subs, data):
    if exists:
        paths, coords = get_paths(paths, subs)

        # save files
        for idx, col in enumerate(COLS):
            shape = data[col][:].shape if col != 'region_labels' else (data[col][:].shape[0], 1)
            data_value = data[col][:] if col != 'region_labels' else [str(x).strip("b'") for x in data[col][:]]
            convert.to_tsv(paths[idx][0], data_value)
            convert.to_json(paths[idx][1], shape, desc='', key='param', coords=coords)

