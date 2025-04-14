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

import os
import sys
from pprint import pformat

from sphinx.util import inspect

import simultipac

# Add the _ext/ folder so that Sphinx can find it
sys.path.append(os.path.abspath("./_ext"))

project = "Simultipac"
author = "Adrien Plaçais"
copyright = "2025, " + author

# See https://protips.readthedocs.io/git-tag-version.html
# The full version, including alpha/beta/rc tags.
# release = re.sub("^v", "", os.popen("git describe").read().strip())
# The short X.Y version.
# version = release
version = simultipac.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "simultipac_sphinx_extensions",  # use :unit: role
    "myst_parser",
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "sphinx_tabs.tabs",
]

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",  # Keep original members order
    "private-members": True,  # Document _private members
    "special-members": "__init__, __post_init__, __str__",  # Document those special members
    "undoc-members": True,  # Document members without doc
}

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
typehints_defaults = "comma"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_sidebars = {
    "**": [
        "versions.html",
    ],
}


# -- Constants display fix ---------------------------------------------------
# https://stackoverflow.com/a/65195854
def object_description(obj: object) -> str:
    """Format the given object for a clearer printing."""
    return pformat(obj, indent=4)


inspect.object_description = object_description
