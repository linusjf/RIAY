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

latex_elements = {
    'preamble': r'''
\usepackage{fontspec}
\usepackage{ucharclasses}

% Main font
\setmainfont{TeX Gyre Termes}

% Emoji fallback font
\newfontfamily\emojifont{Symbola}

% Auto-switch to Symbola for emoji Unicode blocks
\setTransitionsForUnicodeBlock{Emoticons}{\emojifont}{\rmfamily}
\setTransitionsForUnicodeBlock{Supplemental Symbols and Pictographs}{\emojifont}{\rmfamily}
\setTransitionsForUnicodeBlock{Miscellaneous Symbols and Pictographs}{\emojifont}{\rmfamily}
\setTransitionsForUnicodeBlock{Transport and Map Symbols}{\emojifont}{\rmfamily}
    '''
}

latex_elements = {
    'preamble': r'''
\usepackage{fontspec}
\defaultfontfeatures{Renderer=Harfbuzz}

% Set main font with fallback to Symbola for emojis
\setmainfont{TeX Gyre Termes}[
  Path = /usr/share/fonts/truetype/,
  Extension = .ttf,
  UprightFont = *,
  BoldFont = *-Bold,
  ItalicFont = *-Italic,
  BoldItalicFont = *-BoldItalic,
  Emoji = Symbola
]

% Or set up Symbola fallback manually
\newfontfamily\symbolafont{Symbola}

% Optional macro to force emoji font
\newcommand{\emoji}[1]{{\symbolafont #1}}
    '''
}
