# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from io import BytesIO


def fig_to_bytes(fig, form='png'):
    """
    Convert a Matplotlib figure to png (default) or svg bytes.
    """
    buf = BytesIO()
    fig.savefig(buf, format=form)
    buf.seek(0)
    return buf.getvalue()
