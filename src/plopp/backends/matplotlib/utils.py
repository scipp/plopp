# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from io import BytesIO
from typing import Literal

import matplotlib as mpl
from matplotlib.pyplot import Figure, _get_backend_mod

from ..protocols import FigureLike


def fig_to_bytes(fig: Figure, form: Literal['png', 'svg'] = 'png') -> bytes:
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
    Return `True` if the current backend used by Matplotlib is the widget backend.
    """
    return 'ipympl' in mpl.get_backend()


def make_figure(*args, **kwargs) -> Figure:
    """
    Create a new figure.

    If we use ``plt.figure()`` directly, the figures auto-show in the notebooks.
    We want to display the figures when the figure repr is requested.

    When using the static backend, we can return the ``plt.Figure`` (note the uppercase
    F) directly.
    When using the interactive backend, we need to do more work. The ``plt.Figure``
    will not have a toolbar nor will it be interactive, as opposed to what
    ``plt.figure`` returns. We therefore copy the minimal required code inside the
    ``plt.figure`` function which creates a figure manager (which is apparently what
    creates the toolbar and makes the figure interactive).
    """
    if not is_interactive_backend():
        return Figure(*args, **kwargs)
    backend = _get_backend_mod()
    manager = backend.new_figure_manager(1, *args, FigureClass=Figure, **kwargs)
    return manager.canvas.figure


def require_interactive_backend(func: str):
    """
    Raise an error if the current backend in use is non-interactive.
    """
    if not is_interactive_backend():
        raise RuntimeError(
            f"The {func} can only be used with the interactive widget "
            "backend. Use `%matplotlib widget` at the start of your "
            "notebook."
        )


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


def copy_figure(fig: FigureLike, **kwargs) -> FigureLike:
    out = fig.__class__(
        fig._view.__class__,
        *fig._args,
        **{**fig._kwargs, **kwargs},
    )
    for prop in ('xrange', 'yrange', 'xscale', 'yscale', 'title', 'grid'):
        setattr(out.canvas, prop, getattr(fig.canvas, prop))
    return out
