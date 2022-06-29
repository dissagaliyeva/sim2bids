import io
import os
import pandas as pd
from pathlib import Path
import incf.preprocess.preprocess as prep

import time
import sys

sys.path.append('..')

IDS = {}


def check_file(og_path, values, output='../output', save=False):
    subs = {}

    for val in values:
        path = os.path.join(og_path, val)
        name = os.path.basename(val).split('.')[0]

        # create subjects
        subs[val] = {'name': val, 'sid': prep.create_uuid(),
                     'desc': 'default', 'path': path, 'fname': name}
        prep.IDS.append(subs[val]['sid'])

    if save:
        create_output_folder(output, subs)

    layout = create_layout(subs, output)

    return layout

# TODO: create function to determine separators


def save_files(subs, output):
    pass


def create_layout(subs=None, output='../output'):
    """
    Create folder structure according to BEP034 and passed `subs` parameter.

    :param output:
    :param subs:
    :return:
    """

    output = output.replace('.', '').replace('/', '')
    layout = '&emsp;'.join(create_sub(subs))

    return f"""
    {output}/ <br>
        &emsp;|___ code <br>
        &emsp;|___ coord <br>
        &emsp;|___ eq <br>
        &emsp;|___ param <br>
        &emsp;{layout}
        &emsp;|___ README <br>
        &emsp;|___ CHANGES <br>
        &emsp;|___ dataset_description.json <br>
        &emsp;|___ participants.tsv
    """


def create_sub(subs):
    outputs = []
    for k, v in subs.items():
        print(k, v, end='\n\n')

        name = subs[k]['name'].split('.')[0]
        if subs[k]['name'] == 'weights.txt':
            outputs.append(f"""
                    |___ sub-{subs[k]['sid']} <br>
                        &emsp;&emsp;&emsp;|__ net <br>
                            &emsp;&emsp;&emsp;&emsp;|__ sub-{subs[k]['sid']}_desc-{subs[k]['desc']}_{name}.tsv <br>
                            &emsp;&emsp;&emsp;&emsp;|__ sub-{subs[k]['sid']}_desc-{subs[k]['desc']}_{name}.json <br>
                        &emsp;&emsp;&emsp;|__ spatial <br>
                        &emsp;&emsp;&emsp;|__ ts  <br>
                    """)
        elif subs[k]['name'] == 'tract_lengths.txt':
            outputs.append(f"""
                    |___ sub-{subs[k]['sid']} <br>
                         &emsp;&emsp;&emsp;|__ net <br>
                             &emsp;&emsp;&emsp;&emsp;|__ sub-{subs[k]['sid']}_desc-{subs[k]['desc']}_{name}.tsv <br>
                             &emsp;&emsp;&emsp;&emsp;|__ sub-{subs[k]['sid']}_desc-{subs[k]['desc']}_{name}.json <br>
                         &emsp;&emsp;&emsp;|__ spatial <br>
                         &emsp;&emsp;&emsp;|__ ts  <br>
                    """)
    return outputs


# def check_file(fname, content, path='../output', save=False):
#     sid = prep.create_uuid()
#
#     file = fname.split('.')[0] if '.' in fname else fname
#     gen_structure = None
#
#     if file == 'weights':
#         gen_structure = create_layout({
#             'name': file,
#             'desc': 'default',
#             'sid': sid
#         })
#
#     IDS[sid] = {
#         'sid': sid,
#         'uuid': hash(file),
#         'fname': file
#     }
#
#     if save:
#         create_output_folder(sub=f'sub-{sid}')
#         fname = f'sub-{sid}_desc-default_{file}.tsv'
#         # save_file(content, os.path.join(path, f'sub_{sid}', 'net'), sid, fname)
#         # save_file(content, os.path.join(path, f'sub_{sid}', 'net'), sid, fname)
#
#         saving = True
#         while saving:
#             saving = save_file(content, os.path.join(path, f'sub_{sid}', 'net'), sid, fname)
#             # print(os.path.join(path, f'sub_{sid}', 'net'))
#
#     return gen_structure
#
#
# def save_file(content, path, sid, fname, type='.txt'):
#     if not os.path.exists(path):
#         return False
#     print(path)
#     content.to_csv(os.path.join(path, fname), sep='\t', header=None, index=None)
#     Path(os.path.join(path, f'sub_{sid}', 'net', f'{fname}.json')).touch()
#     return True


def create_output_folder(path, subs: dict):
    # verify folders exist
    check_folders(path)

    for k, v in subs.items():
        if k in ['weights.txt', 'distances.txt']:
            create_weights_distances(path, subs[k])


def create_weights_distances(path, subs):
    sub = os.path.join(path, f"sub-{subs['sid']}")
    net = os.path.join(sub, 'net')

    if not os.path.exists(sub):
        print(f'Creating folder `{sub}`')
        os.mkdir(sub)

    if not os.path.exists(net):
        print(f'Creating folder `{net}`')
        os.mkdir(net)

    fname = f'sub-{subs["sid"]}_desc-default_{subs["fname"]}.tsv'

    pd.read_csv(subs['path'], sep='\t').to_csv(os.path.join(net, fname), sep='\t',
                                               header=None, index=None)



def check_folders(path):
    eq = os.path.join(path, 'eq')
    code = os.path.join(path, 'code')
    coor = os.path.join(path, 'coord')
    param = os.path.join(path, 'param')

    for p in [path, eq, code, coor, param]:
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

