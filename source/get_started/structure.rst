Input files and structures
##########################

Accepted file extensions
************************

* txt, csv, dat files
* MATLAB (mat) files (v4 and v6-7.2 using scipy.io.loadmat, v7.3 using mat73 package)
* HDF5 (h5) files
* zip folders containing all above file extensions


Accepted files
**************

Here is the list of files that are supported by the app categorized by their respective folders. Please note the following rules and features:

- the most important file to have for conversions is ``weight`` or ``weights``. It can have ``txt``, ``csv``, or ``dat`` file formats or be stored in MATLAB, H5 files.

.. note::
    Other files are strongly recommended to be present, specifically:
        - ``centres`` (or ``nodes`` and ``labels`` separately),
        - ``distances`` (or ``tract_lengths`` which is the other name for distances, thus this file will be renamed to distances both in the input and output, folders)
        - ``Python code`` that can reproduce the results, and both empirical and simulated time series.

- majority of file names accept singular form naming, e.g., if the file name is ``weight_SC``, it will be recognized as ``weights``. The only exceptions are: ``vertices``, ``nodes``, ``times``, ``faces``, and ``vars``.

- ``average_orientation`` or ``orientation`` will be renamed to ``normals`` `according to BEP034 <https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing>`_ both in the input and output folders.

.. list-table:: Network (net)
   :widths: 30 50 30 50
   :header-rows: 1

   * - File name
     - Description
     - Dimensions
     - Notes
   * - weight
     - The Structural Connectivity that contains the connectome.
     - nxn
     - must be present in the input folder.
   * - distance
     - The distances between areas.
     - nxn
     -
   * - tract_length
     - The distances between areas.
     - nxn
     - will be renamed to ``distance``








.. tabs::

    .. tab:: Network (net)
        ``weight`` → must be present in the input folder (nxn matrix)
            The Structural Connectivity that contains the connectome.
        ``distance`` → should be present in the input folder (nxn matrix)
            The distances between areas.
        ``tract_length`` → should be present in the input folder (nxn matrix)
            **Same as distance**, it's another name for distances. This file will be renamed to "distances" during conversion.
        ``delay`` → good to have in the input folder (nxn matrix)
            The connection delays.
        ``speed`` → good to have in the input folder (nxn matrix)
            The connection speeds.

    .. tab:: Coordinates (coord)
        ``centres`` → should be present in the input folder (nx4 matrix)
            The container storing ``labels`` and ``nodes`` (in this exact sequence).
        ``labels`` → should be present in the input folder (nx1 matrix)
            The region labels that is unique for each individual.
        ``nodes`` → should be present in the input folder (nx3 matrix)
            The 3d coordinate centres that is unique for each individual.
        ``bold_times`` -> should be present in the input folder (nxn matrix)
            The functional connectivity matrix based on BOLD time series.
        ``times`` → should be present in the input folder (nxn matrix)
            The time series of the simulated time series
        ``average_orientation`` or ``orientation`` → good to have in the input folder (nx1 matrix)
            The container for connectivity center orientations. It will be renamed to "normals" in the app.
        ``face`` → good to have in the input folder (nxm matrix)
            The faces of cortex surface shape (triangles, rectangles, ...).
        ``vertices`` ->
        ``vnormal`` →
        ``fnormal`` →
        ``cortical`` →
        ``hemisphere`` →
        ``sensor`` →
        ``map`` →
        ``volume`` →
        ``cartesian2d`` →
        ``cartesian3d`` →
        ``polar2d`` →
        ``polar3d`` →

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
    All contents of MATLAB/H5 files will be extracted and placed in unique subject-specific folders. This hold true for
    subjects both in one folder or unique folders. All extracted files will be saved in txt file format. The overall
    structure should resemble the following:

    .. sourcecode:: python

        |__ 1
            |__ weights.txt
            |__ distances.txt
            |__ emp_fc.txt
            |__ SC_mean_agg.txt

    If the extracted files do not match the app's list of accepted files, you can use the preprocessing pipeline
    specifically created for this purpose. Please visit the following links to learn more:

    * `List of accepted files here <https://sim2bids.readthedocs.io/en/latest/get_started/structure.html#accepted-files>`_

    * `Preprocessing pipeline <https://sim2bids.readthedocs.io/en/latest/get_started/app.html#preprocessing-pipeline>`_


