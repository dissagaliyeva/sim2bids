import os
import shutil


def rm_tree(path: str = '../../output'):
    assert os.path.exists(path), f'Path `{path}` does not exist'

    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)

    print('Removed all test files...')


# def
