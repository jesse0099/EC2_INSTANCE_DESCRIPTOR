import os
import sys
# Path to project modules directory
sys.path.insert(0, os.path.abspath('../../app/'))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EC2 Instances Descriptor'
copyright = '2022, Jese Chavez'
author = 'Jese Chavez'
release = '1.1.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # To automatically generate documentation.
    'sphinx.ext.autodoc',
    # Ability to read documentation from other projects.
    'sphinx.ext.intersphinx'
]
templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
master_doc = 'index'
