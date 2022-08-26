from incf.convert import convert as save_files
from incf.generate import subjects

DEFAULT_TMPL = '{}_desc-{}_{}.{}'


def save(sub, output, folders, end, ses=None):
    file = save_files.open_file(sub['path'], subjects.find_separator(sub['path']))

    if ses is None:
        if end == 'map.txt':
            save_files.save_files(sub, folders[2], file)
        else:
            save_files.save_files(sub, folders[-1], file)
    else:
        if end == 'map.txt':
            save_files.save_files(sub, folders[3], file)
        else:
            save_files.save_files(sub, folders[-1], file)
