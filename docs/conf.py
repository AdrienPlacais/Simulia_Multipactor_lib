# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Simulia Multipactor Library'
copyright = '2023, Adrien Plaçais'
author = 'Adrien Plaçais'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",      # handle numpy style
    "sphinx.ext.autodoc",
    # "sphinx.ext.autosummary",
    "sphinx_rtd_theme",         # ReadTheDocs theme
    "myst_parser",
    "sphinx.ext.todo",          # allow use of TODO
    "nbsphinx",                 # integration of notebooks
    # "sphinx.ext.viewcode",
    # "sphinxcontrib.fulltoc",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True
}

# autosummary_generate = True
add_module_names = False
default_role = 'literal'
todo_include_todos = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'experimental']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "display_version": True,
}
html_static_path = ['_static']


# -- Options for LaTeX output ------------------------------------------------
# https://stackoverflow.com/questions/28454217/how-to-avoid-the-too-deeply-nested-error-when-creating-pdfs-with-sphinx
latex_elements = {
    'preamble': r'\usepackage{enumitem}\setlistdepth{99}'
}
