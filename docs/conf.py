# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import doctest
import os
import sys

import plopp

sys.path.insert(0, os.path.abspath('.'))

# General information about the project.
project = u'plopp'
copyright = u'2023 Scipp contributors'
author = u'Scipp contributors'

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
    "sphinx_design",
    'nbsphinx',
    'sphinx_gallery.load_style',
    'myst_parser',
]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

myst_heading_anchors = 3

autodoc_type_aliases = {
    'VariableLike': 'VariableLike',
    'MetaDataMap': 'MetaDataMap',
    'array_like': 'array_like',
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipp': ('https://scipp.github.io/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'xarray': ('https://xarray.pydata.org/en/stable/', None),
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
source_suffix = ['.rst', '.md']
html_sourcelink_suffix = ''  # Avoid .ipynb.txt extensions in sources

# The master toctree document.
master_doc = 'index'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = plopp.__version__
# The full version, including alpha/beta/rc tags.
release = plopp.__version__

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
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "primary_sidebar_end": ["edit-this-page", "sourcelink"],
    "secondary_sidebar_items": [],
    "show_nav_level": 1,
    "header_links_before_dropdown": 5,
    "pygment_light_style": "github-light-high-contrast",
    "pygment_dark_style": "github-dark-high-contrast",
    "logo": {
        "image_light": "_static/logo.svg",
        "image_dark": "_static/logo-dark.svg",
    },
    "external_links": [
        {"name": "Scipp", "url": "https://scipp.github.io"},
        {"name": "Plopp", "url": "https://scipp.github.io/plopp"},
        {"name": "Scippnexus", "url": "https://scipp.github.io/scippnexus"},
        {"name": "Scippneutron", "url": "https://scipp.github.io/scippneutron"},
        {"name": "ESS", "url": "https://scipp.github.io/ess"},
    ],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/scipp/plopp",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/plopp/",
            "icon": "fa-brands fa-python",
            "type": "fontawesome",
        },
        {
            "name": "Conda",
            "url": "https://anaconda.org/scipp/plopp",
            "icon": "https://scicatproject.github.io/scitacean/_static/"
            "anaconda-logo.svg",
            "type": "url",
        },
    ],
}

html_context = {
    "doc_path": "docs",
}
html_sidebars = {
    "**": ["sidebar-nav-bs", "page-toc"],
}

html_title = "plopp"
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ["css/custom.css"]

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'ploppdoc'

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
doctest_default_flags = (
    doctest.ELLIPSIS
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.DONT_ACCEPT_TRUE_FOR_1
    | doctest.NORMALIZE_WHITESPACE
)

# -- Options for linkcheck ------------------------------------------------

linkcheck_ignore = [
    # Specific lines in Github blobs cannot be found by linkcheck.
    r'https?://github\.com/.*?/blob/[a-f0-9]+/.+?#',
]

# -- Options for nbsphinx gallery------------------------------------------
notebook_root = os.path.join('examples', 'gallery')
thumbnail_root = os.path.join('_static', 'gallery')
nbsphinx_thumbnails = {
    os.path.join(notebook_root, 'nyc-taxi'): os.path.join(
        thumbnail_root, 'nyc-taxi-thumbnail.png'
    ),
    os.path.join(notebook_root, 'masking-a-range'): os.path.join(
        thumbnail_root, 'masking-a-range-thumbnail.png'
    ),
    os.path.join(notebook_root, 'rectangle-selection'): os.path.join(
        thumbnail_root, 'rectangle-selection-thumbnail.png'
    ),
    os.path.join(notebook_root, 'scatter3d-with-threshold'): os.path.join(
        thumbnail_root, 'scatter3d-with-threshold-thumbnail.png'
    ),
    os.path.join(notebook_root, 'scatter3d-with-slider'): os.path.join(
        thumbnail_root, 'scatter3d-with-slider-thumbnail.png'
    ),
}
