import os
import zipfile
import sim2bids.generate.subjects as subj


def extract_zip(path):
    # get folder name
    basename = subj.get_filename(path)

    # get root directory
    parent = path.replace(basename, '')

    # files to extract
    to_extract = ['weights.txt', 'centres.txt', 'tract_lengths.txt', 'average_orientations.txt', 'areas.txt',
                  'cortical.txt', 'hemisphere.txt']

    # get all files within root directory
    contents = os.listdir(parent)

    # if files are already extracted, exit the function
    if to_extract in contents:
        return

    if len(set(to_extract).intersection(set(contents))) != 7:
        # open zip file
        archive = zipfile.ZipFile(path)

        # store all newly added files
        added = []

        # iterate over zip content and extract everything
        for ext in to_extract:
            if ext in archive.namelist():
                # get filename
                new_filename = os.path.join(parent, ext)

                # extract file
                if not os.path.exists(new_filename):
                    archive.extract(ext, path=parent)

                    # rename tract_lengths.txt to distances.txt
                    if ext.startswith('tract_lengths'):
                        new_filename = new_filename.replace('tract_lengths', 'distances')

                        # rename the new file
                        os.replace(os.path.join(parent, ext), new_filename)

                    # append newly added files
                    added.append(new_filename)

        return added
