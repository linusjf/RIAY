# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'RIAY'
copyright = '2025, Linus Fernandes'
author = 'Linus Fernandes'
version = '1'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser"]

templates_path = ['_templates']
exclude_patterns = ["stitch.md","January/*.md","February/*.md", "March/*.md", "April/*.md", "May/*.md", "June/*.md", "July/*.md", "August/*.md", "September/*.md", "October/*.md"\
                    , "November/*.md", "December/*.md","README.md"]
suppress_warnings = ['toc.not_included']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'

html_exclude_files = ['book.rst']
# -- Options for PDF output
latex_engine = 'lualatex'

latex_elements = {
    'preamble': r'''
\usepackage{emoji}
''',
}

latex_documents = [
    ('book', 'riay.tex', 'RIAY content', 'Linus Fernandes', 'manual'),
]

import sphinx

# Default for HTML and EPUB
master_doc = 'index'

# If we're building LaTeX → override master_doc to 'book'
if tags.has('latex'):
    master_doc = 'book'

# If we're building EPUB → exclude book.rst
if tags.has('epub'):
    epub_exclude_files = ['book.rst','README.md']
