import io
import os
import pandas as pd
from pathlib import Path
import incf.preprocess.preprocess as prep

import time
import sys
sys.path.append('..')


IDS = {}


def check_file(fname, content, path='../output', save=False):
    sid = prep.create_uuid()

    file = fname.split('.')[0] if '.' in fname else fname
    gen_structure = None

    if file == 'weights':
        gen_structure = create_layout({
            'name': file,
            'desc': 'default',
            'sid': sid
        })

    IDS[sid] = {
        'sid': sid,
        'uuid': hash(file),
        'fname': file
    }

    if save:
        create_output_folder(sub=f'sub-{sid}')
        fname = f'sub-{sid}_desc-default_{file}.tsv'
        save_file(content, os.path.join(path, f'sub_{sid}', 'net'), sid, fname)
        save_file(content, os.path.join(path, f'sub_{sid}', 'net'), sid, fname)

        saving = True
        while saving:
            saving = save_file(content, os.path.join(path, f'sub_{sid}', 'net'), sid, fname)
            print(os.path.join(path, f'sub_{sid}', 'net'))

    return gen_structure


def save_file(content, path, sid, fname):
    if not os.path.exists(path):
        return False
    print(path)
    content.to_csv(os.path.join(path, fname), sep='\t', header=None, index=None)
    Path(os.path.join(path, f'sub_{sid}', 'net', f'{fname}.json')).touch()
    return True


def create_output_folder(path='../output', sub='sub_00'):
    # verify folders exist
    check_folders(path)

    # patient specific folders
    sub = os.path.join(path, sub)
    net = os.path.join(sub, 'net')

    if not os.path.exists(sub):
        print(f'Creating folder `{sub}`...')
        os.mkdir(sub)

        print(f'Creating folder `{net}`...')
        os.mkdir(net)

        time.sleep(5)

    else:
        # TODO: add create new id creation
        pass


def check_folders(path):
    eq    = os.path.join(path, 'eq')
    code  = os.path.join(path, 'code')
    coor  = os.path.join(path, 'coord')
    param = os.path.join(path, 'param')

    for p in [path, eq, code, coor, param]:
        if not os.path.exists(p):
            print(f'Creating folder `{os.path.basename(p)}`...')
            os.mkdir(p)

    read  = os.path.join(path, 'README.txt')
    part  = os.path.join(path, 'participants.tsv')
    desc  = os.path.join(path, 'dataset_description.json')
    chgs  = os.path.join(path, 'CHANGES.txt')

    for p in [read, part, desc, chgs]:
        if not os.path.exists(p):
            print(f'Creating file `{os.path.basename(p)}`...')
            Path(p).touch()


def create_layout(subs=None):
    """
    Create folder structure according to BEP034 and passed `subs` parameter.

    :param subs:
    :return:
    """

    return f"""
    output/ <br>
        &emsp;|___ code <br>
        &emsp;|___ coord <br>
        &emsp;|___ eq <br>
        &emsp;|___ param <br>
        &emsp;{create_sub(subs)}
        &emsp;|___ README <br>
        &emsp;|___ CHANGES <br>
        &emsp;|___ dataset_description.json <br>
        &emsp;|___ participants.tsv
    """


def create_sub(sub):
    if sub is not None:
        if sub['name'] == 'weights':
            return f"""
            |___ sub-{sub['name']} <br>
                     &emsp;&emsp;&emsp;|__ net <br>
                         &emsp;&emsp;&emsp;&emsp;|__ sub-{sub['sid']}_desc-{sub['desc']}_{sub['name']}.tsv <br>
                         &emsp;&emsp;&emsp;&emsp;|__ sub-{sub['sid']}_desc-{sub['desc']}_{sub['name']}.json <br>
                     &emsp;&emsp;&emsp;|__ spatial <br>
                     &emsp;&emsp;&emsp;|__ ts  <br>
            """

        elif sub['fname'] == 'distances':
            return f"""
                &emsp;|___ sub-{sub['name']} <br>
                     &emsp;&emsp;|__ net <br>
                         &emsp;&emsp;&emsp;|__ sub-{sub['sid']}_desc-{sub['desc']}_{sub['name']}.tsv <br>
                         &emsp;&emsp;&emsp;|__ sub-{sub['sid']}_desc-{sub['desc']}_{sub['name']}.json <br>
                     &emsp;&emsp;|__ spatial <br>
                     &emsp;&emsp;|__ ts  <br>
            """
    return ''
