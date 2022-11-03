#!/usr/bin/env python

"""The setup script."""
from setuptools import setup

requirements = ['numpy', 'pandas', 'h5py', 'panel~=0.13.1', 'holoviews', 'param~=1.12.0',
                'graphviz', 'mat73', 'pylems_py2xml', 'sphinx-tabs', 'sphinx-rtd-theme']

test_requirements = ['pytest>=3']

setup(
    name='sim2bids',
    version='2.0.0',
    description="App to preprocess and convert simulation data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dinara Issagaliyeva",
    author_email='dinarissaa@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Science/Research',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=requirements,
    license="MIT license",
    # long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['simulations', 'computational data', 'BIDS'],
    packages=['sim2bids', 'sim2bids.app', 'sim2bids.convert', 'sim2bids.generate', 'sim2bids.preprocess',
              'sim2bids.templates', 'sim2bids.validate'],
    package_data={'sim2bids': ['generate/models/*.xml']},
    # package_dir={'sim2bids': 'src/sim2bids'},
    url='https://github.com/dissagaliyeva/incf',
    zip_safe=False,
)
