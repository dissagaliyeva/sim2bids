Input files and structures
##########################

Accepted file extensions
************************

* Text files (.txt)
* Tab-separated files (.tsv)
* Generic data files (.dat)
* Numpy array (.npy)
* MATLAB (.mat) files (v4 and v6-7.2 using scipy.io.loadmat, v7.3 using mat73 package)
* HDF5 (.h5) files
* zip folders containing all above file extensions


Required and recommended fields
*******************************

Please note the following rules and recommendations:

- The most important file to have for conversions is **Structural Connectome** which is must be named ``weights``.

- Recommended files:
    - ``centres`` (or ``nodes`` and ``labels`` separately),
    - ``distances`` (or ``tract_lengths`` which is the other name for distances, thus this file will be renamed to distances both in the input and output folders)
    - ``Python``, ``MATLAB`` or ``R`` code that can reproduce the results
    - ``empirical`` and ``simulated`` time series and time stamps.

- ``average_orientation`` or ``orientation`` will be renamed to ``normals`` `according to BEP034 <https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing>`_ both in the input and output folders.


Accepted files
**************

Here is the list of files that are supported by the app categorized by their respective folders.

.. list-table:: Network (``net`` folder)
   :widths: 30 50 30 50
   :header-rows: 1

   * - File name
     - Description
     - Dimensions
     - Notes
   * - weight
     - This is the Structural Connectivity representing the strength of the connection between regions. Zeros represent unconnected areas.
     - nxn
     - must be present in the input folder.
   * - distance
     - These are the length of myelinated fibre tracts between regions in mm.
     - nxn
     - recommended
   * - delays
     - This is the matrix of time delays between regions in physical units, calculated by the following formula: delays = distances / speed.
     - nxn
     - optional
   * - speeds
     - This is a single number or matrix of conduction speeds for the myelinated fibre tracts between regions.
     - optional


.. list-table:: Coordinates (``coord`` folder)
   :widths: 30 50 30 50
   :header-rows: 1

   * - File name
     - Description
     - Dimensions
     - Notes
   * - centres
     - consists of nodes (nx1 vector) and labels (nx3 matrix) in that order.
     - nx4
     - See description of ``nodes`` and ``labels`` below
   * - nodes
     - These are the region labels (e.g., lh_bankssts, lh_superiorfrontal).
     - nx1
     - recommended
   * - delays
     - These are the 3d coordinate centres
     - nx3
     - recommended
   * - times
     - These are the time steps of the simulated time series.
     - nx1
     - recommended
   * - bold_times
     - These are the time steps of the simulated BOLD time series.
     - nx1
     - recommended
   * - areas
     - This is the estimated vector each region's area in mm^2.
     - nx1
     - optional
   * - cortical
     - This is the vector that distinguishes cortical (1) from subcortical (0) regions.
     - nx1
     - optional
   * - average orientations, normals
     - normals.
     - nx3
     - optional. If the file name is ``average_orientation``, it will be named ``normals`` in input and output folders.
   * - hemisphere
     - The vector that distinguishes right (1) from left (0) hemisphere.
     - nx1
     - optional.
   * - faces
     - These are the faces of cortex surface triangulation.
     -
     - optional.
   * - vertices
     - These are the vertices of cortex surface triangulation.
     -
     - optional.
   * - map
     - This is the nxm matrix where the coordinates along rows are mapped to the coordinates along columns.
     - nxm
     - optional.

