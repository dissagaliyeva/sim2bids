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