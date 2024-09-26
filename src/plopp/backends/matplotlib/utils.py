# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from io import BytesIO
from typing import Literal

import matplotlib as mpl
import matplotlib.pyplot as plt


def fig_to_bytes(fig: plt.Figure, form: Literal['png', 'svg'] = 'png') -> bytes:
    """
    Convert a Matplotlib figure to png (default) or svg bytes.

    Parameters
    ----------
    fig:
        The figure to be converted.
    form:
        The format to use.
    """
    buf = BytesIO()
    fig.savefig(buf, format=form, bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()


def is_interactive_backend() -> bool:
    """
    Return ``True`` if the current backend used by Matplotlib creates interactive
    figures. See
    https://matplotlib.org/stable/users/explain/figure/backends.html#the-builtin-backends
    for a list of backends.
    """
    backend = mpl.get_backend().lower()
    return any(
        b in backend
        for b in (
            'qt',
            'ipympl',
            'gtk',
            'tk',
            'wx',
            'nbagg',
            'web',
            'macosx',
            'widget',
            'notebook',
        )
    )


def make_figure(*args, **kwargs) -> plt.Figure:
    """
    Create a new figure.

    If we use ``plt.figure()`` directly, the figures auto-show in the notebooks.
    We want to display the figures when the figure repr is requested.

    When using the static backend, we can return the ``plt.Figure`` (note the uppercase
    F) directly.
    When using the interactive backend, we need to do more work. The ``plt.Figure``
    will not have a toolbar nor will it be interactive, as opposed to what
    ``plt.figure`` returns. To fix this, we need to create a manager for the figure
    (see https://stackoverflow.com/a/75477367).
    """
    fig = plt.Figure(*args, **kwargs)
    if is_interactive_backend():
        # Create a manager for the figure, which makes it interactive, as well as
        # making it possible to show the figure from the terminal.
        plt._backend_mod.new_figure_manager_given_figure(1, fig)
    return fig


def make_legend(leg: bool | tuple[float, float] | str) -> dict:
    """
    Create a dict of arguments to be used in the legend creation.
    """
    return {'loc': leg} if not isinstance(leg, bool) else {}


def _running_in_jupyter() -> bool:
    """
    Detect whether Python is running in Jupyter.

    Note that this includes not only Jupyter notebooks
    but also Jupyter console and qtconsole.
    """
    try:
        import ipykernel.zmqshell
        from IPython import get_ipython
    except ImportError:
        # Cannot be Jupyter if IPython is not installed.
        return False

    return isinstance(get_ipython(), ipykernel.zmqshell.ZMQInteractiveShell)


def is_sphinx_build() -> bool:
    """
    Returns ``True`` if we are running inside a sphinx documentation build.
    """
    if not _running_in_jupyter():
        return False
    from IPython import get_ipython

    ipy = get_ipython()
    cfg = ipy.config
    meta = cfg["Session"]["metadata"]
    if hasattr(meta, "to_dict"):
        meta = meta.to_dict()
    return meta.get("scipp_sphinx_build", False)


def parse_dicts_in_kwargs(kwargs, name):
    out = {}
    for key, value in kwargs.items():
        if isinstance(value, dict):
            if name in value:
                out[key] = value[name]
        else:
            out[key] = value
    return out
