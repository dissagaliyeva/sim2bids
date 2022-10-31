Getting Started
###############

Installation
************

Get the package
===============

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
   from sim2bids.app import app
   pn.extension('tabulator', 'ace', 'jsoneditor', 'ipywidgets', sizing_mode='stretch_width', notifications=True)


Provide software-specific information
=====================================

The main goal of data conversion is to include all information for reproducibility. Therefore, it's required to specify the software name,
version, source code link. For the moment, we explicitly define these variables before starting the app.

Here are some templates that you can use right after import statements. The list will keep getting updated as the app grows.

**TheVirtualBrain (TVB) users**
  .. sourcecode:: python

      # set required fields for current TVB version
      app.SoftwareVersion = 2.6
      app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/2.6'
      app.SoftwareName = 'TVB'


  .. sourcecode:: python

      # set required fields for older TVB versions, e.g. 1.5
      app.SoftwareVersion = 2.6
      app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/1.5.10'
      app.SoftwareName = 'TVB'

.. note::
    Please specify model parameters if you meet one or more of the following conditions:
    * non-Python code (e.g., MATLAB, R, Julia)
    * Python code with more than one rhythm-specific parameters (e.g., separate parameters for alpha and delta rhythms)
    * Python code with a list of parameters (for parameter exploration), e.g., G values from 0.1 to 1.0 with a step of 0.15

    Currently, the app can traverse Python code for one rhythmic parameters only. Supported models with default values as specified in TVB:
    * ReducedWongWang
    * HindmarshRose
    * Generic2dOscillator

    This can be done with the following commands:

    .. sourcecode:: python

        # Example 1: non-Python code
        app.MODEL_NAME = 'ReducedWongWang'
        app.MODEL_PARAMS = dict(a=1., b=2., c=3., G=np.arange(0.1, 1., 0.15))

        # Example 2: Python code with more than one rhythm-specific parameters
        app.MODEL_PARAMS = dict(alpha=dict(a=1., b=3.),
                                delta=dict(a=2., b=1.))

        # Example 3: Python code with a list of parameters
        app.MODEL_PARAMS = dict(G=np.arange(0.1, 1., 0.15))


Run the app
===========

There are two ways to run the app:

**Run locally**
   When you run the app locally (=not on a server, cluster, or anything of the sort), the app creates a localhost page
   in a new tab that will render the app. The page should have a name like this `http://localhost:58838/`, of course,
   with different numbers. Please note that the numbers will keep changing every time you run the app.

   Here is the snippet to run the app:

   .. sourcecode:: python

      pn.serve(MainArea().view())

.. note::
   The app performs best if ran locally. It will open up a new tab running on a local host. It's a known problem
   in the HoloViz community (the package the app built on) that the components **do not** get rendered well if ran inline.


**Run on a server**
  When you run the app on a server/cluster, you will need to run the app inline. The localhost will be created
  but won't be accessible. That's why it's recommended to run it inline.

  Please note that this approach might not work properly because of the rendering issues. You might see text blocked
  but input fields or not be able to do select folders. If you encounter that, please keep restarting the notebook
  until the issue is fixed.

  Here is the snippet to run the app:

  .. sourcecode:: python

      MainArea().view().servable()

.. note::
   We recommend saving all your simulations created on a server and running the app locally for best performance.

Complete script
===============

**Run locally**
  .. sourcecode:: python

      import sim2bids
      import panel as pn
      from sim2bids.sim2bids import MainArea
      pn.extension('tabulator', 'ace', 'jsoneditor', 'ipywidgets', sizing_mode='stretch_width', notifications=True)

      # set required fields
      sim2bids.app.app.SoftwareVersion = 2.6
      sim2bids.app.app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/2.6'
      sim2bids.app.app.SoftwareName = 'TVB'

      pn.serve(MainArea().view())

**Run on a server**
  .. sourcecode:: python

      import sim2bids
      import panel as pn
      from sim2bids.sim2bids import MainArea
      pn.extension('tabulator', 'ace', 'jsoneditor', 'ipywidgets', sizing_mode='stretch_width', notifications=True)

      # set required fields
      sim2bids.app.app.SoftwareVersion = 2.6
      sim2bids.app.app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/2.6'
      sim2bids.app.app.SoftwareName = 'TVB'

      MainArea().view().servable()

