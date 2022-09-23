.. sim2bids documentation master file, created by
   sphinx-quickstart on Thu Sep 22 13:15:18 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sim2bids documentation!
====================================

sim2bids is a Python package to created to convert computational data to BIDS standard as proposed by `Michael Schirner and Petra Ritter. <https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing>`_

The specification proposes a data structure schema for neural network computer models that aims to be generically applicable to all kinds of neural network simulation software, mathematical models, computational models, and data models, but with a focus on dynamic circuit models of brain activity.

Importantly, they not only propose suggestions for a BIDS schema for computer models, but they also propose extensions to the entire BIDS standard that solve several other problems.

.. note::
   This project is under active development.

Installation
============

***************
Get the package
***************

Simply run the following command to get the app up and running:

.. sourcecode:: console

   $ pip install sim2bids

Alternatively, either fork or obtain the latest sim2bids version by running the following:

.. sourcecode:: console

   $ git clone https://github.com/dissagaliyeva/sim2bids
   $ cd sim2bids
   $ python setup.py install

Then, open up your notebook and import the following packages to set up the notebook:

.. sourcecode:: python

   import sim2bids
   import panel as pn
   from sim2bids.sim2bids import MainArea
   pn.extension('tabulator', 'ace', 'jsoneditor', 'ipywidgets', sizing_mode='stretch_width', notifications=True)


*************************************
Provide software-specific information
*************************************

The main goal of data conversion is to include all information for reproducibility. Therefore, it's required to specify the software name,
version, and source code link. For the moment, we explicitly define these variables before starting the app.

Here are some templates that you can use right after import statements. The list will keep getting updated as the app grows.


**TheVirtualBrain (TVB) users**
   .. sourcecode:: python

      # set required fields
      sim2bids.app.app.SoftwareVersion = 2.6
      sim2bids.app.app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/2.6'
      sim2bids.app.app.SoftwareName = 'TVB'


**MATLAB users**
   .. sourcecode:: python

      # set required fields
      sim2bids.app.app.SoftwareVersion = 'R2022b'
      sim2bids.app.app.SoftwareRepository = 'https://www.mathworks.com'
      sim2bids.app.app.SoftwareName = 'MATLAB'







.. toctree::
   :maxdepth: 2
   :caption: Contents:

Table of Contents
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
