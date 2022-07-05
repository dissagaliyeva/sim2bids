import io
import os
import pandas as pd
from pathlib import Path
import incf.preprocess.preprocess as prep
import incf.templates.templates as temp

import json
import sys
import csv
from scipy.io import loadmat
import scipy
import mat73
import h5py

sys.path.append('..')
SID = None


def check_file(og_path, values, output='../output', save=False):
    # create dictionary to store values
    subs = {}

    for val in values:
        # get the absolute path
        path = os.path.join(og_path, val)

        # get filename without file extension
        name = os.path.basename(val).split('.')[0]

        # create subjects
        subs[val] = {'name': val, 'sid': SID, 'sep': find_separator(path),
                     'desc': 'default', 'path': path, 'fname': name}
        if subs[val]['fname'] in ['tract_lengths', 'tract_length']:
            subs[val]['fname'] = 'distances'

        # add new id to make sure there's no overlap in folder creation
        prep.IDS.append(subs[val]['sid'])

    # create folders if required
    if save:
        create_output_folder(output, subs)

    # generate folder structure layout
    layout = create_layout(subs, output)

    return layout


def find_separator(path):
    """
    Find the separator/delimiter used in the file to ensure no exception
    is raised while reading files.

    :param path:
    :return:
    """
    if path.endswith('.mat'): return

    sniffer = csv.Sniffer()

    with open(path) as fp:
        try:
            delimiter = sniffer.sniff(fp.read(5000)).delimiter
        except Exception:
            delimiter = sniffer.sniff(fp.read(100)).delimiter
    return delimiter


def create_layout(subs=None, output='../output'):
    """
    Create folder structure according to BEP034 and passed `subs` parameter.

    :param output:
    :param subs:
    :return:
    """

    output = output.replace('.', '').replace('/', '')
    layout = create_sub(subs)
    layout = '&emsp;'.join(layout) if len(layout) > 1 else ''.join(layout)

    return f"""
    {output}/ <br>
        &emsp;|___ code <br>
        &emsp;|___ eq <br>
        &emsp;|___ param <br>
        &emsp;{layout}
        &emsp;|___ README <br>
        &emsp;|___ CHANGES <br>
        &emsp;|___ dataset_description.json <br>
        &emsp;|___ participants.tsv
    """


def create_sub(subs):
    # centers_found, wd_found, sid = False, False, None
    centers_found, wd_found = False, False
    struct = []

    sub_struct = """|___ sub-{} <br>
    &emsp;&emsp;&emsp;|___ net <br>
    &emsp;&emsp;&emsp;|___ spatial <br>
    &emsp;&emsp;&emsp;|___ ts <br>
    """

    for k, v in subs.items():
        name, desc = subs[k]['fname'], subs[k]['desc']

        if subs[k]['name'] in ['weights.txt', 'tract_lengths.txt', 'tract_length.txt', 'distances.txt']:
            if not wd_found:
                struct += [f'|___ sub-{SID} <br>', '&emsp;&emsp;&emsp;|___ net <br>']
                wd_found = True

            struct.append(f'&emsp;&emsp;&emsp;&emsp;|___ sub-{SID}_desc-{desc}_{name}.json <br>')
            struct.append(f'&emsp;&emsp;&emsp;&emsp;|___ sub-{SID}_desc-{desc}_{name}.tsv <br>')

        if subs[k]['path'].endswith('.mat'):
            if not wd_found:
                struct.append(sub_struct.format(SID))
                wd_found = True

            struct.append(f'&emsp;&emsp;&emsp;&emsp;|___ sub-{SID}_desc-{desc}_{name}.json <br>')
            struct.append(f'&emsp;&emsp;&emsp;&emsp;|___ sub-{SID}_desc-{desc}_{name}.tsv <br>')

        if subs[k]['name'] in ['centres.txt', 'centers.txt']:
            centers_found = True
            struct.append(f"""|___ coord <br>
            &emsp;&emsp;&emsp;|___ desc-{desc}_nodes.json <br>
            &emsp;&emsp;&emsp;|___ desc-{desc}_nodes.tsv <br>
            &emsp;&emsp;&emsp;|___ desc-{desc}_labels.json <br>
            &emsp;&emsp;&emsp;|___ desc-{desc}_labels.tsv <br>
            """)

    # TODO: verify correct consecutive order
    # struct[0] = struct[0].format(SID)
    # struct.append(['&emsp;&emsp;&emsp;|___ spatial <br>', '&emsp;&emsp;&emsp;|___ ts <br>'])

    if not centers_found:
        struct.append('|___ coord <br>')

    return struct


def create_output_folder(path, subs: dict):
    # verify folders exist
    check_folders(path)

    for k, v in subs.items():
        if k in ['weights.txt', 'tract_lengths.txt']:
            create_weights_distances(path, subs[k])
        if k in ['centres.txt', 'centers.txt', 'centre.txt', 'center.txt']:
            create_centers(path, subs[k])
        if k.endswith('.mat'):
            create_simulations(path, subs[k])
        if k.endswith('.h5'):
            create_h5(path, subs[k])


def create_weights_distances(path, subs):
    sub, net, spatial, ts = create_sub_struct(path, subs)

    fname = f'sub-{subs["sid"]}_desc-{subs["desc"]}_{subs["fname"]}'

    f = pd.read_csv(subs['path'], sep=subs['sep'], index_col=None, header=None)
    f.to_csv(os.path.join(net, fname + '.tsv'), sep='\t', header=None, index=None)

    # get info on centers
    coord_files = os.path.exists(os.path.join(path, 'coord', f'desc-{subs["desc"]}_labels.json'))

    if coord_files:
        coords = [f'../coord/desc-{subs["desc"]}_labels.json', f'../coord/desc-{subs["desc"]}_nodes.json']
    else:
        coords = None

    create_json(os.path.join(net, fname + '.json'), f.shape, desc='', ftype='wd', coords=coords)


def create_sub_struct(path, subs):
    sub = os.path.join(path, f"sub-{subs['sid']}")
    net = os.path.join(sub, 'net')
    spatial = os.path.join(sub, 'spatial')
    ts = os.path.join(sub, 'ts')

    for folder in [sub, net, spatial, ts]:
        if not os.path.exists(folder):
            print(f'Creating folder `{folder}`')
            os.mkdir(folder)

    return sub, net, spatial, ts


def create_centers(path, subs):
    f = pd.read_csv(subs['path'], sep=subs['sep'], index_col=None, header=None)
    labels, nodes = f[0], f[[1, 2, 3]]

    # save in `.tsv` format
    labels.to_csv(os.path.join(path, 'coord', f'desc-{subs["desc"]}_labels.tsv'), sep='\t', header=None, index=None)
    nodes.to_csv(os.path.join(path, 'coord', f'desc-{subs["desc"]}_nodes.tsv'), sep='\t', header=None, index=None)

    # save in `.json` format
    desc = subs['desc']
    for content in ['labels', 'nodes']:
        cols = 1 if content == 'labels' else 3
        fpath = os.path.join(path, 'coord', f'desc-{desc}_{content}.json')
        create_json(fpath, [labels.shape[0], cols], 'Time steps of the simulated time series.', 'centers')


def create_simulations(path, subs):
    try:
        mat = loadmat(subs['path'], squeeze_me=True)
    except NotImplementedError:
        print(f'File `{subs["path"]}` uses MATLAB version 7.3. Using appropriate libraries...')
    except scipy.io.matlab._miobase.MatReadError:
        print(f'File `{subs["path"]}` is empty! Aborting file creation...')
    else:
        # mat = mat if not error else mat73.loadmat(subs['path'])
        data = find_mat_array(mat)
        if len(data) == 1:
            data = mat[data]
        # elif len(data) > 1:


        # create_sub_folders(path)
        #
        # fname = f'sub-{SID}_desc-{subs["desc"]}-{subs["fname"]}.tsv'
        # pd.DataFrame(mat[data]).to_csv(os.path.join(path, f'sub-{SID}', 'ts', fname), sep='\t', header=None, index=None)
        #
        # fpath = os.path.join(path, 'coord', f'desc-{subs["desc"]}_times.json')
        # create_json(fpath, mat[data].shape, 'Time steps of the simulated time series.', 'simulations')


def create_json(fpath, shape, desc, ftype, coords=None):
    json_file = None

    if ftype == 'simulations':
        json_file = temp.merge_dicts(temp.JSON_template, temp.JSON_simulations)
    elif ftype == 'centers':
        json_file = temp.JSON_centers
    elif ftype == 'wd':
        json_file = temp.JSON_template

    if json_file is not None:
        with open(fpath, 'w') as f:
            json.dump(temp.populate_dict(json_file, shape=shape, desc=desc, coords=coords), f)


def find_mat_array(mat):
    data = []

    for k, v in mat.items():
        if type(v) not in [bytes, str, list]:
            data.append(k)

    return data


def create_h5(path, subs):
    data = h5py.File(subs['path'])
    vals = ['weights', 'tract_lengths', 'region_labels', 'centres']
    sub, net, spatial, ts = create_sub_struct(path, subs)

    default = 'sub-{}_desc-{}_{}.{}'
    sid, desc, fname = subs['sid'], subs['desc'], subs['fname']

    # TODO: finish the iteration
    paths = [os.path.join(net, default.format(sid, desc, fname, 'tsv')),
             os.path.join(net, default.format(sid, desc, fname, 'json')),
             os.path.join(path, 'coord', default.format(sid, ))]

    if len(set(vals).intersection(set(data.keys()))) == 4:
        for val in vals:
            pd.DataFrame(data[val][:]).to_csv()


def create_sub_folders(path):
    sub = os.path.join(path, f'sub-{SID}')
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
