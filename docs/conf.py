# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import doctest
import os
import sys
from datetime import date
from typing import Any, Dict, Optional

import sphinx_book_theme
from docutils.nodes import document
from sphinx.application import Sphinx

import plopp

sys.path.insert(0, os.path.abspath('.'))

from version import VersionInfo  # noqa: E402

# General information about the project.
project = u'plopp'
copyright = u'2023 Scipp contributors'
author = u'Scipp contributors'

version_info = VersionInfo()
long_version = plopp.__version__
outdated = not version_info.is_latest(long_version)


def add_buttons(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: Dict[str, Any],
    doctree: Optional[document],
):
    base = "https://scipp.github.io"
    l1 = []
    l1.append({"type": "link", "text": "scipp", "url": f"{base}"})
    l1.append({"type": "link", "text": "plopp", "url": f"{base}/plopp"})
    l1.append({"type": "link", "text": "scippnexus", "url": f"{base}/scippnexus"})
    l1.append({"type": "link", "text": "scippneutron", "url": f"{base}/scippneutron"})
    l1.append({"type": "link", "text": "ess", "url": f"{base}/ess"})
    header_buttons = context["header_buttons"]
    header_buttons.append({
        "type": "group",
        "buttons": l1,
        "icon": "fa fa-caret-down",
        "text": "Related projects"
    })
    releases = version_info.minor_releases(first='0.1')
    if outdated:
        current = f"{long_version} (outdated)"
        latest = "latest"
        entries = ['.'.join(long_version.split('.')[:2])]
    else:
        current = f"{long_version} (latest)"
        latest = f"{releases[0]} (latest)"
        entries = releases[1:]
    lines = [{"type": "link", "text": latest, "url": f"{base}/{project}"}]
    for r in entries:
        lines.append({
            "type": "link",
            "text": f"{r}",
            "url": f"{base}/{project}/release/{r}"
        })
    header_buttons.append({
        "type": "group",
        "buttons": lines,
        "icon": "fa fa-caret-down",
        "text": current
    })


sphinx_book_theme.add_launch_buttons = add_buttons

html_show_sourcelink = True

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
    'nbsphinx',
    'sphinx_gallery.load_style',
]

autodoc_type_aliases = {
    'VariableLike': 'VariableLike',
    'MetaDataMap': 'MetaDataMap',
    'array_like': 'array_like',
}

rst_epilog = f"""
.. |SCIPP_RELEASE_MONTH| replace:: {date.today().strftime("%B %Y")}
.. |SCIPP_VERSION| replace:: {plopp.__version__}
"""  # noqa: E501

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipp': ('https://scipp.github.io/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'xarray': ('https://xarray.pydata.org/en/stable/', None)
}

# autodocs includes everything, even irrelevant API internals. autosummary
# looks more suitable in the long run when the API grows.
# For a nice example see how xarray handles its API documentation.
autosummary_generate = True

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = False
napoleon_preprocess_types = True
napoleon_type_aliases = {
    # objects without namespace: scipp
    "DataArray": "~scipp.DataArray",
    "Dataset": "~scipp.Dataset",
    "Variable": "~scipp.Variable",
    # objects without namespace: numpy
    "ndarray": "~numpy.ndarray",
}
typehints_defaults = 'comma'
typehints_use_rtype = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'
html_sourcelink_suffix = ''  # Avoid .ipynb.txt extensions in sources

# The master toctree document.
master_doc = 'index'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = u''
# The full version, including alpha/beta/rc tags.
release = u''

warning_is_error = True

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = 'sphinx_book_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    "logo_only": True,
    "repository_url": f"https://github.com/scipp/{project}",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "show_toc_level": 2,  # Show subheadings in secondary sidebar
}

if outdated:
    html_theme_options["announcement"] = (
        f"⚠️ You are viewing the documentation for an old version of {project}. "
        f"Switch to <a href='https://scipp.github.io/{project}' "
        "style='color:white;text-decoration:underline;'"
        ">latest</a> version. ⚠️")

html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'ploppdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'scipp.tex', u'scipp Documentation', u'Simon Heybrock', 'manual'),
]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, 'scipp', u'scipp Documentation', [author], 1)]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'scipp', u'scipp Documentation', author, 'scipp',
     'One line description of project.', 'Miscellaneous'),
]

# -- Options for Matplotlib in notebooks ----------------------------------

nbsphinx_execute_arguments = [
    "--Session.metadata=scipp_sphinx_build=True",
]

# -- Options for doctest --------------------------------------------------

doctest_global_setup = '''
import numpy as np
import scipp as sc
'''

# Using normalize whitespace because many __str__ functions in scipp produce
# extraneous empty lines and it would look strange to include them in the docs.
doctest_default_flags = doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL | \
                        doctest.DONT_ACCEPT_TRUE_FOR_1 | \
                        doctest.NORMALIZE_WHITESPACE

# -- Options for linkcheck ------------------------------------------------

linkcheck_ignore = [
    # Specific lines in Github blobs cannot be found by linkcheck.
    r'https?://github\.com/.*?/blob/[a-f0-9]+/.+?#',
]

# -- Options for nbsphinx gallery------------------------------------------

nbsphinx_thumbnails = {
    'examples/gallery/nyc-taxi':
    '_static/gallery/nyc-taxi-thumbnail.png',
    'examples/gallery/masking-a-range':
    '_static/gallery/masking-a-range-thumbnail.png',
    'examples/gallery/rectangle-selection':
    '_static/gallery/rectangle-selection-thumbnail.png',
    'examples/gallery/scatter3d-with-threshold':
    '_static/gallery/scatter3d-with-threshold-thumbnail.png',
}
