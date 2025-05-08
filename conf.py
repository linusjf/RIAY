# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "RIAY"
copyright = "2025, Linus Fernandes"
author = "Linus Fernandes"
version = "1"
release = "1.0"
master_doc = "index"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinxcontrib.cairosvgconverter", "sphinx_rtd_dark_mode", "sphinx_rtd_theme"]

templates_path = ["_templates"]
include_patterns = ["index.rst", "*.md",  "*/*.jpg"]
exclude_patterns = [
    "stitch.md",
    "January/*.md",
    "February/*.md",
    "March/*.md",
    "April/*.md",
    "May/*.md",
    "June/*.md",
    "July/*.md",
    "August/*.md",
    "September/*.md",
    "October/*.md",
    "November/*.md",
    "December/*.md",
    "README.md",
    "Conventions/*.md",
    ".aider.chat*",
]
suppress_warnings = ["toc.not_included", "myst.xref_missing", "image/svg+xml"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = "alabaster"
html_theme = "sphinx_rtd_theme"
# user starts in dark mode
default_dark_mode = True

# -- Options for PDF output
latex_engine = "lualatex"

latex_elements = {
    "fontpkg": r"""
        \usepackage{fontspec}
    """,
    "preamble": r"""
\pdfminorversion=7
\setmainfont{Symbola}
""",
}

# -- Options for linkcheck
linkcheck_timeout = 30  # seconds
linkcheck_ignore = [
    r"http://localhost:\d+/",  # Ignore local dev servers
    r"https://example\.com/redirect",  # Ignore known redirect
    r"https://raw.githubusercontent.com/linusjf/RIAY/",
    r"https://www.gnu.org/software/m4/m4.html",
]
linkcheck_ignore_redirects = True
linkcheck_workers = 2  # or even 1 to be safer
linkcheck_retries = 2

# hook to replace unavailable emojis in Symbola
# for available ones only during pdf latex generation
import os
import codecs


def replace_emojis_in_file(file_path):
    replacements = {
        "🥹": "😢",
        "🥰": "😍",
    }

    try:
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with codecs.open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def replace_emojis_in_markdown():
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".md"):
                replace_emojis_in_file(os.path.join(dirpath, filename))


def run_only_for_pdf(app):
    if app.builder.name == "latex":  # "latexpdf" invokes the "latex" builder
        print("Running emoji replacement for PDF build...")
        replace_emojis_in_markdown()


def setup(app):
    app.connect("builder-inited", run_only_for_pdf)
