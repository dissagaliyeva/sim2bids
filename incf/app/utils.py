"""
Helper functions for app.py
"""


def rename_tract_lengths(file: str) -> str:
    if 'tract_lengths' in file:
        return file.replace('tract_lengths', 'distances')
    return file

