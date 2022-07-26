def extract_zip(path):
    # get folder name
    basename = subj.get_filename(path)

    parent = path.replace(basename, '')

    # get the suffix (ses-preop or ses-postop)
    suffix = get_suffix(path)

    # open zip file
    archive = zipfile.ZipFile(path)

    # store all newly added files
    added = []

    # iterate over zip content and extract only the files that are included in TO_EXRACT
    for ext in TO_EXTRACT:
        if ext in archive.namelist():
            # add the suffix to the newly extracted file
            new_filename = os.path.join(parent, add_suffix(ext, suffix))

            # rename tract_lengths.txt to distances.txt
            if 'tract_lengths' in new_filename:
                new_filename = new_filename.replace('tract_lengths', 'distances')

            if not os.path.exists(new_filename):
                # extract new file
                archive.extract(ext, path=parent)

                # rename the new file
                os.replace(os.path.join(parent, ext), new_filename)

                # remove tract_lengths: get the path
                tract_path = os.path.join(parent, f'tract_lengths_{suffix}.txt')

                # remove tract_lengths
                if os.path.exists(tract_path):
                    os.remove(tract_path)

                # append newly added files
                added.append(new_filename)

    return added


def verify_zip_rename(files):
    match = ['weights', 'distances', 'centres']

    for idx, file in enumerate(files):
        basename = os.path.basename(file)
        base_split = basename.split('.')[0]

        if ('preop' not in basename or 'postop' not in basename) and base_split in match:
            suffix = get_suffix(file)
            files[idx] = add_suffix(file, suffix)

    return list(set(files))


def get_suffix(path):
    return os.path.dirname(path).split('\\')[-1].split('-')[-1]


def add_suffix(filename, suffix):
    return filename.replace('.', f'_{suffix}.')
