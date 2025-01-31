# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Build info --------------------------------------------------------------
# From project base, generate the rst files with:
# sphinx-apidoc -o docs/simultipac -f -e -M src/ -d 5
# cd docs/simultipac
# nvim *.rst
# :bufdo %s/^\(\S*\.\)\(\S*\) \(package\|module\)/\2 \3/e | update
# cd ../..
# sphinx-multiversion docs ../.simultipac-docs/html

# If you want unversioned doc:
# make html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from __future__ import annotations

import simultipac

project = "Simultipac"
copyright = "2025, Adrien Plaçais"
author = "Adrien Plaçais"

# See https://protips.readthedocs.io/git-tag-version.html
# The full version, including alpha/beta/rc tags.
# release = re.sub("^v", "", os.popen("git describe").read().strip())
# The short X.Y version.
# version = release
version = simultipac.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # "sphinxcontrib.bibtex",  # Integrate citations
    "sphinx.ext.napoleon",  # handle numpy style
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",  # ReadTheDocs theme
    "myst_parser",
    "sphinx.ext.intersphinx",  # interlink with other docs, such as numpy
    "sphinx.ext.todo",  # allow use of TODO
    "nbsphinx",
    "sphinx_autodoc_typehints",  # Printing types in docstrings not necessary anymore
    "sphinx_tabs.tabs",
]

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",  # Keep original members order
    "private-members": True,  # Document _private members
    "special-members": "__init__, __post_init__, __str__",  # Document those special members
    "undoc-members": True,  # Document members without doc
}

# autosummary_generate = True
add_module_names = False
default_role = "literal"
todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "experimental",
    "simultipac/modules.rst",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
}
html_static_path = ["_static"]

# -- Check that there is no broken link --------------------------------------
nitpicky = False
nitpick_ignore = [
    # Not recognized by Sphinx, don't know if this is normal
    ("py:class", "optional"),
    ("py:class", "T"),
]

# Link to other libraries
intersphinx_mapping = {
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "vedo": ("https://vedo.embl.es/docs/", None),
}

# Parameters for sphinx-autodoc-typehints
always_document_param_types = True
always_use_bar_union = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_sidebars = {
    "**": [
        "versions.html",
    ],
}


# -- Options for LaTeX output ------------------------------------------------
# https://stackoverflow.com/questions/28454217/how-to-avoid-the-too-deeply-nested-error-when-creating-pdfs-with-sphinx
latex_elements = {"preamble": r"\usepackage{enumitem}\setlistdepth{99}"}
