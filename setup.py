#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

# with open('README.rst') as readme_file:
#     readme = readme_file.read()
#
# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

requirements = ['numpy', 'pandas', 'h5py', 'panel~=0.13.1', 'holoviews', 'param~=1.12.0',
                'graphviz', 'mat73', 'pylems_py2xml']

test_requirements = ['pytest>=3']

setup(
    name='sim2bids',
    version='0.0.14',
    description="App to preprocess and convert simulation data",
    author="Dinara Issagaliyeva",
    author_email='dinarissaa@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=requirements,
    license="MIT license",
    # long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['simulations', 'computational data', 'Holoviz Panel'],
    packages=['sim2bids', 'sim2bids.app', 'sim2bids.convert', 'sim2bids.generate', 'sim2bids.preprocess',
              'sim2bids.templates', 'sim2bids.validate'],
    # package_dir={'sim2bids': 'src/sim2bids'},
    url='https://github.com/dissagaliyeva/incf',
    zip_safe=False,
)
