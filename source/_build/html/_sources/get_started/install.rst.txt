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

This app aims to help you and future users reproduce the results of your simulations. Specify the required fields before
running the app to make the process easier. Please note that the fields **are case-sensitive**:

.. class:: custom_heading

MODEL_NAME
    Name of the model used in your simulation. Currently accepted models: *ReducedWongWang*, *HindmarshRose*, and *Generic2dOscillator*. The models follow the same default values as specified in TheVirtualBrain.

    * `ReducedWongWang <https://docs.thevirtualbrain.org/api/tvb.contrib.scripts.models.html?highlight=reducedwongwang#module-tvb.contrib.scripts.models.reduced_wong_wang_exc_io>`_

        a=270.0, b=108.0, d=0.154, gamma=0.000641, tau_s=100.0, w=0.9, J_N=0.2609, I_o=0.3, G=2.0, sigma_noise=1.e-09, tau_rin=100

    * `HindmarshRose <https://docs.thevirtualbrain.org/api/tvb.contrib.simulator.models.html?highlight=hindmarshrose#module-tvb.contrib.simulator.models.hindmarsh_rose>`_

        r=0.001, a=1.0, b=3.0, c=1.0, d=5.0, s=1.0, x_1=-1.6

    * `Generic2dOscillator <https://docs.thevirtualbrain.org/api/tvb.contrib.simulator.models.html?highlight=hindmarshrose#module-tvb.contrib.simulator.models.generic_2d_oscillator>`_

        tau=1.25, a=1.05, b=0.2, omega=1.0, upsilon=1.0, gamma=1.0, eta=1.0

    **Example**:

    .. sourcecode:: python

            app.MODEL_NAME = 'ReducedWongWang'

.. class:: custom_heading

MODEL_PARAMS
    Model parameters used in the code. **If you have a Python file with up to one rhythm, the app supplements parameters without assistance**.

    Please manually specify model parameters if the code meets one of the following conditions:

    * non-Python code (e.g., MATLAB, R, Julia)

    * Python code with more than one rhythm-specific parameters (e.g., separate parameters for alpha and delta rhythms)

    * Python code with a list of parameters (for parameter exploration), e.g., G values from 0.1 to 1.0 with a step of 0.15

    Example code for each cases above:

    .. sourcecode:: python

        # Example 1: non-Python code
        app.MODEL_NAME = 'ReducedWongWang'
        app.MODEL_PARAMS = dict(a=1., b=2., c=3., G=np.arange(0.1, 1., 0.15))

        # Example 2: Python code with more than one rhythm-specific parameters
        app.MODEL_PARAMS = dict(alpha=dict(a=1., b=3.),
                                delta=dict(a=2., b=1.))

        # Example 3: Python code with a list of parameters
        app.MODEL_PARAMS = dict(G=np.arange(0.1, 1., 0.15))





Here are some templates that you can use right after import statements. The list will keep getting updated as the app grows.

**TheVirtualBrain (TVB) users**
  .. sourcecode:: python

      # set required fields for current TVB version
      app.SoftwareVersion = 2.6
      app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/2.6'
      app.SoftwareName = 'TVB'


  .. sourcecode:: python

      # set required fields for older TVB versions, e.g. 1.5.10
      app.SoftwareVersion = '1.5.10'
      app.SoftwareRepository = 'https://github.com/the-virtual-brain/tvb-root/releases/tag/1.5.10'
      app.SoftwareName = 'TVB'

.. warning::
    Please specify model parameters if your input code meets one of the following conditions:

    * non-Python code (e.g., MATLAB, R, Julia)

    * Python code with more than one rhythm-specific parameters (e.g., separate parameters for alpha and delta rhythms)

    * Python code with a list of parameters (for parameter exploration), e.g., G values from 0.1 to 1.0 with a step of 0.15

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

