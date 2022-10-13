# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from contextlib import contextmanager
from io import BytesIO
import matplotlib as mpl


def fig_to_bytes(fig, form='png'):
    """
    Convert a Matplotlib figure to png (default) or svg bytes.
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
