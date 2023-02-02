# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from contextlib import contextmanager
from io import BytesIO
from typing import Literal

import matplotlib as mpl
from matplotlib.pyplot import Figure


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


@contextmanager
def silent_mpl_figure():
    """
    Context manager to prevent automatic generation of figures in Jupyter.
    """
    backend_ = mpl.get_backend()
    revert = False
    if 'inline' in backend_:
        mpl.use("Agg")
        revert = True
    with mpl.pyplot.ioff():
        yield
    if revert:
        mpl.use(backend_)


def is_interactive_backend():
    """
    Return `True` if the current backend used by Matplotlib is the widget backend.
    """
    return 'ipympl' in mpl.get_backend()


def require_interactive_backend(func: str):
    """
    Raise an error if the current backend in use is non-interactive.
    """
    if not is_interactive_backend():
        raise RuntimeError(f"The {func} can only be used with the interactive widget "
                           "backend. Use `%matplotlib widget` at the start of your "
                           "notebook.")


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
