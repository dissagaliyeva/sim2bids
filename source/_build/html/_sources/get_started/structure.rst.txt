Input files and structures
##########################

Accepted file extensions
************************

* txt, csv, dat files
* mat, MATLAB files (v4 and v6-7.2 using scipy.io.loadmat, v7.3 using mat73 package)
* h5, HDF5 files
* zip folders containing all above file extensions


Accepted files
**************

.. tabs::

    .. tab:: Network (net)
        ``weights`` → Structural connectivity that contains the connectome.

    .. tab:: Coordinates (coord)


    .. tab:: Time series (ts)


    .. tab:: Spatial


    .. tab:: Code



Accepted structures
*******************

There are quite a few structures that are supported by the app:

Single-subject inputs
=====================

.. rst-class:: special

**Single subject without sessions**
  This structure supports either a list of files or a directory storing the files. For example, it could look like:

    .. sourcecode:: python

        |__ weights.[txt|dat|csv]
        |__ distances.[txt|dat|csv]
        |__ centres.[txt|dat|csv]

    .. sourcecode:: python

        |__ folder_name
            |__ weights.[txt|dat|csv]
            |__ distances.[txt|dat|csv]
            |__ centres.[txt|dat|csv]

.. rst-class:: special

**Single subject with sessions**
  This structure is like the structure above but with the additional folder(s) *ses-preop* and *ses-postop*.
  If you have one of the session types, make sure to pass the **entire folder**. For example, if your folder structure follows
  the layout below, make sure to select *ses-preop* folder or go back one level and select *sub-01*.

  **It does not matter how you name the subject folder**, it will automatically be assumed it's a single-subject folder.

    .. sourcecode:: python

        |__ sub-01
            |__ ses-preop
                |__ weights.[txt|dat|csv]
                |__ distances.[txt|dat|csv]
                |__ centres.[txt|dat|csv]

    Alternatively, you can pass both *ses-preop* and *ses-postop* folders at once or go one level up and pass the whole folder
    containing the subject with both sessions.

Multi-subject inputs
====================

.. rst-class:: special

**MATLAB/H5 files**
  This structure accepts MATLAB/H5 files containing all information about a single subject. They can be either all in the
  same folder or stored in their own respective folders. For example:

  #. Single-folder
        .. sourcecode:: python

            |__ 1.mat
            .
            .
            .
            |__ N.mat

  #. Multi-folder
        .. sourcecode:: python

            |__ 1
                |__ 1.mat
            .
            .
            .
            |__ N
                |__ N.mat

  .. note::
    All contents of MATLAB/H5 files will be extracted and placed in unique subject-specific folders. This is applicable
    for both structures where subjects are in unique folders or all subjects in one folder. The extracted structure should look like this:

    .. sourcecode:: python

        |__ 1
            |__ weights.txt
            |__ distances.txt
            |__ emp_fc.txt
            |__ SC_mean_agg.txt

    **Beware that everything inside the structure will be extracted**. The files that are understood by the app will be converted. Preprocessing
    the rest is your responsibility. We accounted for this scenario and created a preprocessing pipeline for your convenience. See the links below to learn more:

    * `List of accepted files here <https://sim2bids.readthedocs.io/en/latest/get_started/structure.html#accepted-files>`_

    * `Preprocessing pipeline <https://sim2bids.readthedocs.io/en/latest/get_started/app.html#preprocessing-pipeline>`_


