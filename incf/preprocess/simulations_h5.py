import os
import h5py
import incf.preprocess.generate as gen

COLS = ['weights', 'tract_lengths', 'region_labels', 'centres']


class XML:
    def __init__(self, path, output_folder):
        self.path = path
        self.params = []
        self.output_folder = output_folder
        self.file, self.keys = None, None
        self.template = """<?xml version="1.0" ?>
<Lems xmlns="http://www.neuroml.org/lems/0.7.6" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.neuroml.org/lems/0.7.6 https://raw.githubusercontent.com/LEMS/LEMS/development/Schemas/LEMS/LEMS_v0.7.6.xsd">
    <Component {}/>
</Lems>"""
        self.parse_file()

    def parse_file(self):
        if self.path.endswith('.h5'):
            self.file = h5py.File(self.path)
            self.keys = list(self.file.keys())

            for k in self.keys:
                self.params.append('{}="{}"'.format(k, self.file[k][:][0]))

            print(f'Found following parameters:\n{self.keys}')
            self.create_xml()

    def create_xml(self):
        if len(self.params) > 0:
            self.template = self.template.format(' '.join(self.params))
            with open(self.output_folder, 'w') as f:
                f.write(self.template)


def create(path, subs):
    # open h5 file
    data = h5py.File(subs['path'])

    # create subject-specific folders
    _, net, _, _ = gen.create_sub_struct(path, subs)

    # check if `param` values exist
    create_params(check_params(data), [path, net], subs, data)


def check_params(data):
    # check if all the columns are present
    return len(set(COLS).intersection(set(data.keys()))) == 4


def get_paths(paths, subs):
    path, net = paths
    sid, desc, fname = subs['sid'], subs['desc'], subs['fname'].split('_')[0].lower()

    paths = [
        [os.path.join(net, gen.DEFAULT_TMPL.format(sid, desc, f'{fname}-weights', 'tsv')),
         os.path.join(net, gen.DEFAULT_TMPL.format(sid, desc, f'{fname}-weights', 'json'))],
        [os.path.join(net, gen.DEFAULT_TMPL.format(sid, desc, f'{fname}-distances', 'tsv')),
         os.path.join(net, gen.DEFAULT_TMPL.format(sid, desc, f'{fname}-distances', 'json'))],
        [os.path.join(path, 'coord', gen.COORD_TMPL.format(desc, f'{fname}_labels', 'tsv')),
         os.path.join(path, 'coord', gen.COORD_TMPL.format(desc, f'{fname}_labels', 'json'))],
        [os.path.join(path, 'coord', gen.COORD_TMPL.format(desc, f'{fname}_nodes', 'tsv')),
         os.path.join(path, 'coord', gen.COORD_TMPL.format(desc, f'{fname}_nodes', 'json'))]
    ]

    return paths, [f'../coords/{fname}_labels.json', f'../coords/{fname}_nodes.json']


def create_params(exists, paths, subs, data):

    if exists:
        paths, coords = get_paths(paths, subs)

        # save files
        for idx, col in enumerate(COLS):
            shape = data[col][:].shape if col != 'region_labels' else (data[col][:].shape[0], 1)
            data_value = data[col][:] if col != 'region_labels' else [str(x).strip("b'") for x in data[col][:]]
            gen.to_tsv(data_value, paths[idx][0])
            gen.to_json(paths[idx][1], shape, desc='', ftype='simulations', coords=coords)

