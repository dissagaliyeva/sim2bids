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

    def iterate(self, k, v, ses=None, sid=None):
        sid = v['sid'] if sid is None else sid

        if sid not in self.components['subjects'] and ses is None:
            self.components['subjects'][sid] = {'net': [], 'ts': [], 'spatial': []}

        # save weights, distances, and centres
        if ses is None:
            if k in ['weights.txt', 'distances.txt', 'tract_lengths.txt']:
                self.save_wd(v, sid)
            elif k == 'centres.txt':
                self.save_centres(v, sid)
            elif k.endswith('.mat'):
                self.save_mat(v, sid)
            elif k.endswith('.h5'):
                self.save_h5(v)
        else:
            for k2, v2 in v.items():
                if k2 in ['weights.txt', 'distances.txt']:
                    self.save_wd(v2, sid, ses=ses)
                elif k2 in ['centers.txt']:
                    self.save_centres(v2, sid, ses=ses)
                elif k2 in convert.TO_EXTRACT[3:]:
                    self.save_sub_coord(v2, sid, ses=ses)
                elif k2.endswith('.mat'):
                    self.save_mat(v2, sid, ses=ses)
                elif k2.endswith('.h5'):
                    self.save_h5(v2, ses=ses)

    def save_wd(self, v, sid, ses=None):
        if ses is None:
            self.components['subjects'][sid]['net'] += common_structure(v)
        else:
            self.components['subjects'][sid][ses]['net'] += common_structure(v)

    def save_centres(self, v, sid, ses=None):
        if ses is None:
            self.components['coord'] += coord_structure(v)
        else:
            del self.components['coord']
            self.components['subjects'][sid][ses]['coord'] += coord_structure(v)

    def save_sub_coord(self, v, sid, ses):
        self.components['subjects'][sid][ses]['coord'] += coord_structure(v, v['name'])

    def save_mat(self, v, sid, ses=None):
        if ses is None:
            self.components['subjects'][sid]['ts'] += common_structure(v)
            self.components['subjects'][sid]['coord'] += [coord_format.format(v['desc'], 'times', 'tsv'),
                                                          coord_format.format(v['desc'], 'times', 'json')]
        else:
            self.components['subjects'][sid][ses]['ts'] += common_structure(v)
            self.components['subjects'][sid][ses]['coord'] += [coord_format.format(v['desc'], 'times', 'tsv'),
                                                               coord_format.format(v['desc'], 'times', 'json')]

    def save_h5(self, v, ses=None):
        file = h.File(v['path'])
        keys = file.keys()
        name = v['fname'].split('_')[0].lower()

        if ses is None:
            sid = v['sid']
            if sid not in self.components['subjects']:
                self.components['subjects'][sid] = {'net': [], 'ts': [], 'spatial': []}

            if sim.check_params(file):
                self.components['subjects'][sid]['net'] += common_structure(v, 'weights')
                self.components['subjects'][sid]['net'] += common_structure(v, 'distances')
                self.components['coord'] += coord_structure(v)
            else:
                if len(list(keys)) > 0:
                    self.components['param'] += [coord_format.format(v['desc'], name, 'xml'),
                                                 coord_format.format(v['desc'], name, 'json')]

    def populate(self):
        ses_exists = False
        for k, v in self.subs.items():
            if 'sid' in v:
                # traverse single-instance files
                self.iterate(k, v)
            else:
                for k2, v2 in v.items():
                    if k not in self.components['subjects'].keys() and k2 in ['ses-preop', 'ses-postop']:
                        self.components['subjects'][k] = OrderedDict(
                            {'ses-preop': {'net': [], 'ts': [], 'spatial': [], 'coord': []},
                             'ses-postop': {'net': [], 'ts': [], 'spatial': [], 'coord': []}})

                    if k2 == 'ses-preop':
                        ses_exists = True
                        self.iterate(k2, v2, sid=k, ses='ses-preop')
                    if k2 == 'ses-postop':
                        ses_exists = True
                        self.iterate(k2, v2, sid=k, ses='ses-postop')
                    if k2 not in ['ses-preop', 'ses-postop']:
                        self.iterate(k2, v2)
                        self.components['coord'] = list(set(self.components['coord']))

        if ses_exists:
            self.create_ses_layout()
        else:
            self.create_layout()

    def join(self, files, form='files'):
        subfile = '&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|___{}<br>'
        sub2file = '&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|___{}<br>'
        file = '&emsp;&emsp;&emsp;&emsp;|___{}<br>'
        joiner = lambda x: ''.join(x)

        if form == 'files':
            return joiner([file.format(f) for f in files])
        elif form == 'sub':
            return joiner([sub2file.format(f) for f in files])
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

    def create_ses_layout(self):
        fold = '&emsp;&emsp;|___{}/<br>'
        subfold = '&emsp;&emsp;&emsp;&emsp;|___{}/<br>'
        main_files = '|___{}<br>'

        self.layout.append('|___ output/<br>')

        for k, v in self.components.items():
            if isinstance(v, list) and k != 'files':
                self.layout += [fold.format(k), self.join(v)]
            elif isinstance(v, dict):
                for k2, v2 in v.items():

                    self.layout += [fold.format(f'sub-{k2}')]

                    for k3 in v2.keys():
                        if len(v2[k3]['net']) == 0:
                            continue
                        self.layout += [subfold.format(k3),
                                        '&emsp;&emsp;' + subfold.format('net'), self.join(v2[k3]['net'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('ts'), self.join(v2[k3]['ts'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('spatial'), self.join(v2[k3]['spatial'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('coord'), self.join(v2[k3]['coord'], 'sub')]

        self.layout += [main_files.format(x) for x in self.components['files']]
        self.layout = ''.join(self.layout)
        print(self.layout)


def common_structure(v, name=None):
    name = v['name'] if name is None else name

    return [default_format.format(v['sid'], v['desc'], name, 'tsv'),
            default_format.format(v['sid'], v['desc'], name, 'json')]


def coord_structure(v, name=None):
    if name is None:
        return [coord_format.format(v['desc'], 'nodes', 'tsv'),
                coord_format.format(v['desc'], 'nodes', 'json'),
                coord_format.format(v['desc'], 'labels', 'tsv'),
                coord_format.format(v['desc'], 'labels', 'json')]
    return [coord_format.format(v['desc'], name, 'tsv'),
            coord_format.format(v['desc'], name, 'json')]


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
