import os.path
import shutil


def rm_tree(path: str = '../../output'):
    assert os.path.exists(path), f'Path `{path}` does not exist'

    print('Removing all test files...')
    shutil.rmtree(path)
