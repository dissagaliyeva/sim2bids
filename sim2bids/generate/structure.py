import os
import re

import h5py as h
from pathlib import Path
from sim2bids.app import app
from collections import OrderedDict
import sim2bids.app.utils as utils

default_format, coord_format = '{}_desc-{}_{}.{}', 'desc-{}_{}.{}'


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
        self.default_format = '{}_desc-{}_{}.{}'
        self.coord_format = 'desc-{}_{}.{}'
        self.populate()

    def iterate(self, k, v, ses=None, sid=None):
        sid = v['sid'] if sid is None else sid

        # save weights, distances, and centres
        for k2, v2 in v.items():
            self.iterate_dict(k2, v2, sid, ses=ses)

    def iterate_dict(self, k, v, sid, ses=None):
        k = k.split('_')[-1] if '_' in k else k

        if k in ['weights.txt', 'distances.txt', 'tract_lengths.txt']:
            self.save_wd(v, sid, ses=ses)
        elif k in ['centres.txt']:
            self.save_centres(v, sid, ses=ses)
        elif k in ['map.txt']:
            self.save_map(v, sid, ses=ses)
        elif k in ['nodes.txt', 'labels.txt', *app.TO_EXTRACT[3:], 'times.txt']:
            self.save_centres(v, sid, ses=ses, name=v['name'])
        elif k.split('.')[0] in ['ts', 'emp', 'vars', 'stimuli', 'noise', 'spikes', 'raster', 'events']:
            self.save_mat(v, sid, ses=ses)
        elif k.endswith('.mat') or k.split('.')[0] in ['fc', 'bold']:
            if 'fc' in k.lower():
                self.save_mat(v, sid, ses=ses, fc=True)
            else:
                self.save_mat(v, sid, ses=ses)
        elif k.endswith('.h5'):
            self.save_h5(v, ses=ses)

        if app.CODE is not None:
            self.save_code(v)

    def save_wd(self, v, sid, ses=None):
        structure = common_structure(v)

        if ses is None:
            if len(set(structure).intersection(set(self.components['subjects'][sid]['net']))) == 0:
                self.components['subjects'][sid]['net'] += structure
        else:
            if len(set(structure).intersection(set(self.components['subjects'][sid][ses]['net']))) == 0:
                self.components['subjects'][sid][ses]['net'] += structure

    def save_map(self, v, sid, ses=None):
        if ses is None:
            if app.MULTI_INPUT:
                self.components['subjects'][sid]['spatial'] += common_structure(v, 'map')
            else:
                self.components['subjects']['spatial'] += coord_structure(v, ses)
        else:
            self.components['subjects'][sid][ses]['spatial'] += common_structure(v, 'map')

    def save_centres(self, v, sid, ses=None, name=None):
        structure = coord_structure(v, ses) if name is None else common_structure(v, name)

        if ses is None:
            if app.MULTI_INPUT:
                if len(self.components['subjects'][sid]['coord']) == 0:
                    self.components['subjects'][sid]['coord'] += coord_structure(v, ses='multi')
            else:
                if len(set(structure).intersection(set(self.components['coord']))) == 0:
                    self.components['coord'] += structure
        else:
            if len(set(structure).intersection(set(self.components['subjects'][sid][ses]['coord']))) == 0:
                self.components['subjects'][sid][ses]['coord'] += structure

    def save_mat(self, v, sid, ses=None, fc=False):
        name, desc = v['name'].lower(), v['desc']

        if ses is None:
            if fc:
                self.components['subjects'][sid]['spatial'] += common_structure(v, name)
            else:
                self.components['subjects'][sid]['ts'] += common_structure(v, name)
        else:
            if fc:
                self.components['subjects'][sid][ses]['spatial'] += [
                    coord_format.replace('desc-', '').format(f'{sid}_desc-{desc}', name, 'tsv'),
                    coord_format.replace('desc-', '').format(f'{sid}_desc-{desc}', name, 'json')]
            else:
                self.components['subjects'][sid][ses]['ts'] += common_structure(v)

    def save_h5(self, v, ses=None):
        file = h.File(v['path'])
        keys = file.keys()
        name = v['fname'].split('_')[0].lower()

        if ses is None:
            sid = v['sid']
            if sid not in self.components['subjects']:
                self.components['subjects'][sid] = {'net': [], 'ts': [], 'spatial': [], 'map': [], 'coord': []}

            if len(set(app.TO_EXTRACT).intersection(set(file.keys()))) > 1:
                self.components['subjects'][sid]['net'] += common_structure(v, 'weights')
                self.components['subjects'][sid]['net'] += common_structure(v, 'distances')

                if not app.MULTI_INPUT:
                    self.components['coord'] += coord_structure(v)
                else:
                    del self.components['coord']
            else:
                pass
                # if len(list(keys)) > 0:
                #     self.components['param'] += [coord_format.format(v['desc'], name, 'xml'),
                #                                  coord_format.format(v['desc'], name, 'json')]

    def save_code(self, v):
        self.components['code'] = [self.coord_format.format(app.DESC, 'code', 'json'),
                                   self.coord_format.format(app.DESC, 'code', 'py')]
        self.components['eq'] = [self.coord_format.format(app.DESC, 'eq', 'json'),
                                 self.coord_format.format(app.DESC, 'eq', 'xml')]
        self.components['param'] = [
            self.coord_format.format(app.DESC, 'param', 'json'),
            self.coord_format.format(app.DESC, 'param', 'xml')
        ]

    def populate(self):
        ses_exists = False

        for k, v in self.subs.items():
            if ('sid' in v or not app.MULTI_INPUT) and ('ses-preop' not in v.keys() and 'ses-postop' not in v.keys()):

                if k not in self.components['subjects'].keys():
                    self.components['subjects'][k] = {'net': [], 'ts': [], 'spatial': [], 'coord': [], 'map': []}
                    # traverse single-instance files
                    self.iterate(k, v, sid=k)
            else:
                for k2, v2 in v.items():
                    if k not in self.components['subjects'].keys():
                        if k2 in ['ses-preop', 'ses-postop']:
                            self.components['subjects'][k] = {
                                'ses-preop': {'net': [], 'ts': [], 'spatial': [], 'coord': [], 'map': []},
                                'ses-postop': {'net': [], 'ts': [], 'spatial': [], 'coord': [], 'map': []}
                            }
                        else:
                            self.components['subjects'][k] = {
                                'net': [], 'ts': [], 'spatial': [], 'coord': [], 'map': []
                            }

                    if k2 == 'ses-preop':
                        ses_exists = True
                        self.iterate(k2, v2, sid=k, ses='ses-preop')
                    if k2 == 'ses-postop':
                        ses_exists = True
                        self.iterate(k2, v2, sid=k, ses='ses-postop')
                    if k2 not in ['ses-preop', 'ses-postop']:
                        if k.endswith('txt') or k.endswith('csv') or k.endswith('mat') or k.endswith('h5'):
                            self.iterate_dict(k, v, sid=v['sid'])
                        else:
                            self.iterate(k, v, sid=k)
                            # self.components['coord'] = list(set(self.components['coord']))

        self.components = verify_structure(self.components)

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
                        self.layout += [fold.format(f'{k2}'),
                                        subfold.format('net'), self.join(v2['net'], 'subfile'),
                                        subfold.format('ts'), self.join(v2['ts'], 'subfile'),
                                        subfold.format('spatial'), self.join(v2['spatial'], 'subfile'),
                                        subfold.format('map'), self.join(v2['map'], 'subfile'),
                                        subfold.format('coord'), self.join(v2['coord'], 'subfile')]

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

                    self.layout += [fold.format(k2)]

                    for k3 in v2.keys():
                        if len(v2[k3]['net']) == 0:
                            continue
                        self.layout += [subfold.format(k3),
                                        '&emsp;&emsp;' + subfold.format('net'), self.join(v2[k3]['net'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('ts'), self.join(v2[k3]['ts'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('spatial'), self.join(v2[k3]['spatial'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('coord'), self.join(v2[k3]['coord'], 'sub'),
                                        '&emsp;&emsp;' + subfold.format('map'), self.join(v2[k3]['map'], 'sub')]

        self.layout += [main_files.format(x) for x in self.components['files']]
        self.layout = ''.join(self.layout)


def verify_structure(dictionary):
    temp = dictionary.copy()

    for k, v in dictionary.items():
        if not k.startswith('sub-') and isinstance(v, list):
            for idx, v2 in enumerate(v):
                if v2.startswith('sub-'):
                    match = re.match('sub-[0-9]+', v2)[0]
                    temp[k][idx] = v2.replace(match, '').strip('_')

    return temp


def common_structure(v, name=None):
    name = v['name'].lower() if name is None else name.lower()

    return [default_format.format(v['sid'], v['desc'], name, 'tsv'),
            default_format.format(v['sid'], v['desc'], name, 'json')]


def coord_structure(v, ses=None):
    sid, desc = v['sid'], v['desc']

    if ses is None:
        return [coord_format.format(desc, 'nodes', 'tsv'),
                coord_format.format(desc, 'nodes', 'json'),
                coord_format.format(desc, 'labels', 'tsv'),
                coord_format.format(desc, 'labels', 'json')]
    return [default_format.format(sid, desc, 'nodes', 'tsv'),
            default_format.format(sid, desc, 'nodes', 'json'),
            default_format.format(sid, desc, 'labels', 'tsv'),
            default_format.format(sid, desc, 'labels', 'json')]


def create_layout(subs=None, output='output'):
    """
    Create folder structure according to BEP034 and passed `subs` parameter.
    :param output:
    :param subs:
    :return:
    """

    output = output.replace('.', '').replace('/', '')
    return FolderStructure(output, subs).layout


def check_folders(path):
    eq = os.path.join(path, 'eq')
    code = os.path.join(path, 'code')
    coord = os.path.join(path, 'coord')
    param = os.path.join(path, 'param')

    for p in [path, eq, code, coord, param]:
        if not os.path.exists(p):
            os.mkdir(p)

    read = os.path.join(path, 'README.txt')
    part = os.path.join(path, 'participants.tsv')
    desc = os.path.join(path, 'dataset_description.json')
    chgs = os.path.join(path, 'CHANGES.txt')

    for p in [read, part, desc, chgs]:
        if not os.path.exists(p):
            Path(p).touch()
