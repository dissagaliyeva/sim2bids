import os
import pandas as pd

from incf.app import app


# define naming conventions
DEFAULT_TEMPLATE = '{}_desc-{}_{}.{}'
COORD_TEMPLATE = 'desc-{}_{}.{}'


def save(subs, folders, ses=None, name=None):
    """

    :param subs:
    :param folders:
    :param ses:
    :param name:
    :return:
    """

    # get folder location for weights and distances
    if name == 'wd':
        if ses is None:
            folder = folders[1]
        else:
            folder = folders[2]

    # get folder location for centres
    if name == 'centres':
        # check if all centres are of the same content
        pass


def check_centres():
    # get all centres files
    centres = get_specific('centres')

    #


def get_specific(filetype: str) -> list:
    """
    Get all files that correspond to the filetype. For example,
    if filetype is equal to "areas", this function will return
    all files containing that keyword.

    :param filetype:
    :return:
    """

    content = []

    for file in app.ALL_FILES:
        if filetype in file:
            content.append(file)

    return content


def open_file(path: str, sep: str):
    """

    :param path:
    :param sep:
    :return:
    """
    try:
        f = pd.read_csv(path, sep=sep, header=None, index_col=False)
    except pd.errors.EmptyDataError:
        return ''
    except ValueError:
        return ''
    else:
        return f
