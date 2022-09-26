Input files and structures
##########################

Accepted file extensions
========================

* txt, csv, dat files
* mat, MATLAB files (v4 and v6-7.2 using scipy.io.loadmat, v7.3 using mat73 package)
* h5, HDF5 files
* zip folders containing all above file extensions


Accepted structures
===================

There are quite a few structures that are supported by the app:

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
