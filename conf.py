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
master_doc = 'index'

# Default for HTML and EPUB

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser","sphinxcontrib.cairosvgconverter"]

templates_path = ['_templates']
exclude_patterns = ["stitch.md","January/*.md","February/*.md", "March/*.md", "April/*.md", "May/*.md", "June/*.md", "July/*.md", "August/*.md", "September/*.md", "October/*.md"\
                    , "November/*.md", "December/*.md","README.md", "Conventions/*.md", ".aider.chat*"]
suppress_warnings = ['toc.not_included','myst.xref_missing','image/svg+xml']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'

# -- Options for PDF output
latex_engine = 'lualatex'

latex_elements = { 
        'fontpkg': r'''
        \usepackage{fontspec}
    ''',
    'preamble': r'''
\pdfminorversion=7
\setmainfont{Symbola}
''',
 }

