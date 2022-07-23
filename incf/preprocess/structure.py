import os
import h5py as h
from pathlib import Path
from incf.convert import convert
from collections import OrderedDict
from incf.preprocess import simulations_h5 as sim

default_format, coord_format = 'sub-{}_desc-{}_{}.{}', 'desc-{}_{}.{}'


class FolderStructure:
    def __init__(self, path, subs):
        self.path = path
        self.subs = subs

        self.components = OrderedDict({
            'code': [],
            'coord': [],
            'eq': [],
            'param': [],
            'subjects': {},
            'files': ['CHANGES.txt', 'dataset_description.json', 'participants.tsv', 'README.txt']
        })

        self.layout = []
        self.default_format = 'sub-{}_desc-{}_{}.{}'
        self.coord_format = 'desc-{}_{}.{}'
        self.populate()

    def common_structure(self, v, name=None):
        name = v['name'] if name is None else name
        return [self.default_format.format(v['sid'], v['desc'], name, 'tsv'),
                self.default_format.format(v['sid'], v['desc'], name, 'json')]

    def coord_structure(self, v):
        return [self.coord_format.format(v['desc'], 'nodes', 'tsv'),
                self.coord_format.format(v['desc'], 'nodes', 'json'),
                self.coord_format.format(v['desc'], 'labels', 'tsv'),
                self.coord_format.format(v['desc'], 'labels', 'json')]

    def iterate(self, k, v):
        sid = v['sid']
        if sid not in self.components['subjects']:
            self.components['subjects'][sid] = {'net': [], 'ts': [], 'spatial': []}

        if k in ['weights.txt', 'distances.txt', 'tract_lengths.txt',
                 'weights_preop.txt', 'distances_preop.txt', 'tract_lengths_preop.txt',
                 'weights_postop.txt', 'distances_postop.txt', 'tract_lengths_postop.txt']:
            self.components['subjects'][sid]['net'] += self.common_structure(v)
        elif k in ['centers.txt', 'centers_preop.txt', 'centres_preop.txt',
                   'centers_postop.txt', 'centres_postop.txt', 'centers_postop.txt']:
            self.components['coord'] += self.coord_structure(v)
        elif k.endswith('.mat'):
            self.components['subjects'][sid]['ts'] += self.common_structure(v)
            self.components['coord'] += [self.coord_format.format(v['desc'], 'times', 'tsv'),
                                         self.coord_format.format(v['desc'], 'times', 'json')]
        elif k.endswith('.h5'):
            file = h.File(v['path'])
            keys = file.keys()
            name = v['fname'].split('_')[0].lower()

            sid = v['sid']
            if sid not in self.components['subjects']:
                self.components['subjects'][sid] = {'net': [], 'ts': [], 'spatial': []}

            if sim.check_params(file):
                self.components['subjects'][sid]['net'] += self.common_structure(v, 'weights')
                self.components['subjects'][sid]['net'] += self.common_structure(v, 'distances')
                self.components['coord'] += self.coord_structure(v)
            else:
                if len(list(keys)) > 0:
                    self.components['param'] += [self.coord_format.format(v['desc'], name, 'xml'),
                                                 self.coord_format.format(v['desc'], name, 'json')]

    def populate(self):
        for k, v in self.subs.items():
            if 'sid' in v:
                # traverse single-instance files
                self.iterate(k, v)
            else:
                for k2, v2 in v.items():
                    self.iterate(k2, v2)
        self.components['coord'] = list(set(self.components['coord']))
        self.create_layout()

    def join(self, files, form='files'):
        subfile = '&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|___{}<br>'
        file = '&emsp;&emsp;&emsp;&emsp;|___{}<br>'
        joiner = lambda x: ''.join(x)

        if form == 'files':
            return joiner([file.format(f) for f in files])
        return joiner([subfile.format(f) for f in files])

    def create_layout(self):
        fold = '&emsp;&emsp;|___{}/<br>'
        subfold = '&emsp;&emsp;&emsp;&emsp;|___{}/<br>'
        main_files = '|___{}<br>'

        self.layout.append('|___ output/<br>')

        for k, v in self.components.items():
            if len(v) == 0:
                self.layout.append(fold.format(k))
            else:
                if isinstance(v, list) and k != 'files':
                    self.layout += [fold.format(k), self.join(v)]
                elif isinstance(v, dict):
                    for k2, v2 in v.items():
                        self.layout += [fold.format(f'sub-{k2}'), subfold.format('net'),
                                        self.join(v2['net'], 'subfile'), subfold.format('ts'),
                                        self.join(v2['ts'], 'subfile'), subfold.format('spatial'),
                                        self.join(v2['spatial'], 'subfile')]

        self.layout += [main_files.format(x) for x in self.components['files']]
        self.layout = ''.join(self.layout)


def common_structure(v, name=None):
    name = v['name'] if name is None else name
    return [default_format.format(v['sid'], v['desc'], name, 'tsv'),
            default_format.format(v['sid'], v['desc'], name, 'json')]


def coord_structure(v):
    return [coord_format.format(v['desc'], 'nodes', 'tsv'),
            coord_format.format(v['desc'], 'nodes', 'json'),
            coord_format.format(v['desc'], 'labels', 'tsv'),
            coord_format.format(v['desc'], 'labels', 'json')]


def create_layout(subs=None, output='../output'):
    """
    Create folder structure according to BEP034 and passed `subs` parameter.
    :param output:
    :param subs:
    :return:
    """

    output = output.replace('.', '').replace('/', '')
    return FolderStructure(output, subs).layout


def create_sub_folders(path):
    sub = os.path.join(path, f'sub-{convert.SID}')
    net = os.path.join(sub, 'net')
    ts = os.path.join(sub, 'ts')
    spatial = os.path.join(sub, 'spatial')

    for file in [sub, net, ts, spatial]:
        if not os.path.exists(file):
            os.mkdir(file)


def check_folders(path):
    eq = os.path.join(path, 'eq')
    code = os.path.join(path, 'code')
    coord = os.path.join(path, 'coord')
    param = os.path.join(path, 'param')

    for p in [path, eq, code, coord, param]:
        if not os.path.exists(p):
            print(f'Creating folder `{os.path.basename(p)}`...')
            os.mkdir(p)

    read = os.path.join(path, 'README.txt')
    part = os.path.join(path, 'participants.tsv')
    desc = os.path.join(path, 'dataset_description.json')
    chgs = os.path.join(path, 'CHANGES.txt')

    for p in [read, part, desc, chgs]:
        if not os.path.exists(p):
            print(f'Creating file `{os.path.basename(p)}`...')
            Path(p).touch()
