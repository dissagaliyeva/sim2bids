# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sphinx_rtd_theme

on_rtd = os.environ.get("READTHEDOCS") == "True"

project = 'sim2bids'
copyright = '2022, Dinara Issagaliyeva'
author = 'Dinara Issagaliyeva'
release = '1.1.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = ['sphinx_rtd_theme', 'sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
              'sphinx.ext.autosummary', 'sphinx.ext.extlinks', 'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode', 'sphinx.ext.inheritance_diagram', 'sphinx.ext.githubpages',
              'sphinx.ext.autosectionlabel',
              ]

# Make sure the target is unique
autosectionlabel_prefix_document = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

master_doc = "index"
source_suffix = ".rst"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
if on_rtd:
    # managed automatically by rtd
    pass
else:
    html_theme = "sphinx_rtd_theme"

html_theme_path = ["_themes"]
html_static_path = ['_static']
