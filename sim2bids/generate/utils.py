"""
Model parameters based on The Virtual Brain (TVB)'s parameters. Details can be found here:
https://docs.thevirtualbrain.org/_modules/tvb/simulator/models

Currently supported models: ReducedWongWang, HindmarshRose, Generic2dOscillator

"""

import os
import sys
sys.path.append('')


TVB_MODELS = {
    'SJHM3D': {
        'name': 'hindmarsh_rose',
        'desc': 'These are the equations to simulate the time series with the'
                'Stefanescu-Jirsa 3D (reduced Hindmarsh-Rose model) model.',
        'params': dict(r=[0.006], a=[1.], b=[3.], c=[1.], d=[5.], s=[1.], xo=[-1.6], K11=[0.5],
                       K12=[0.1], K21=[0.15], sigma=[0.3], mu=[3.3], x_1=[-1.6], A_ik=None,
                       B_ik=None, C_ik=None, a_i=None, b_i=None, c_i=None, d_i=None, e_i=None, f_i=None,
                       h_i=None, p_i=None, IE_i=None, II_i=None, m_i=None, n_i=None,
                       variables_of_interest=['xi', 'eta', 'tau'],
                       state_variable_range=dict(x=[-4., 4.], y=[-60., 20.], z=[-2., 18.], eta=[-25., 20.0],
                                                 alpha=[-4., 4.], beta=[-20., 20.], gamma=[2., 10.]))
    },
    'G2DOS': {
        'name': 'generic_oscillator',
        'desc': 'These are the equations to simulate the time series with the Generic2dOscillator model.',
        'params': dict(tau=[1.], I=[0.1], a=[0.5], b=[0.4], c=[-4.], d=[0.02], e=[3.], f=[1.],
                       g=[0.], alpha=[1.], beta=[1.], gamma=[1.])
    },
    'RWW': {
        'name': 'reduced_wong_wang',
        'desc': 'These are the equations to simulate the time series with the Reduced Wong Wang model.',
        'params': dict(a=270., b=108., d=0.154, gamma=0.000641, tau_s=100., w=0.9, J_N=0.2609, I_o=0.3,
                       G=2., sigma_noise=1.e-09, tau_rin=100)
    }
}


# open file and prepare the dataset
def open_file(path: str) -> list:
    """

    :param path:
    :return:
    """

    # verify the path exists
    assert os.path.exists(path), f'File at location {path} does not exist'

    # define an array to store line-by-line iteration
    contents = []

    # open file
    with open(path) as file:
        # iterate over lines of code and pick the relevant lines only
        for line in file.readlines():
            # ignore comments, empty lines, and imports
            if not line.startswith('#') and not line.startswith('import') and \
                    not line.startswith('from') and line != '\n':
                # save relevant lines
                contents.append(line.strip('\n').strip())

    return contents


def preprocess_params(dictionary: dict) -> dict:
    temp = {}

    for k, v in dictionary.items():
        if isinstance(v, list) and len(v) == 1:
            temp[k] = v[0]
        else:
            temp[k] = v

    return temp
