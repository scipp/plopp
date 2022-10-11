# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .common import is_interactive_backend


def figure(*args, **kwargs):
    """
    Make a figure that is either static or interactive depending on the backend in use.
    """
    if is_interactive_backend():
        from ..graphics import InteractiveFig
        return InteractiveFig(*args, **kwargs)
    else:
        from ..graphics import StaticFig
        return StaticFig(*args, **kwargs)


def figure2d(*args, **kwargs):
    """
    Make a figure that is either static or interactive depending on the backend in use.
    """
    if is_interactive_backend():
        from ..graphics import InteractiveFig2d
        return InteractiveFig2d(*args, **kwargs)
    else:
        from ..graphics import StaticFig2d
        return StaticFig2d(*args, **kwargs)
