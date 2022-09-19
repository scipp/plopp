# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import is_interactive_backend


def figure(*args, **kwargs):
    """
    Make a figure that is either static or interactive depending on the backend in use.
    """
    if is_interactive_backend():
        from ..interactive import InteractiveFig
        return InteractiveFig(*args, **kwargs)
    else:
        from ..static import StaticFig
        return StaticFig(*args, **kwargs)
