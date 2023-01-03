# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .utils import is_interactive_backend


def figure1d(*args, **kwargs):

    if is_interactive_backend():
        from .interactive import InteractiveFig1d
        return InteractiveFig1d(*args, **kwargs)
    else:
        from .static import StaticFig
        return StaticFig(*args, **kwargs)


def figure2d(*args, **kwargs):

    if is_interactive_backend():
        from .interactive import InteractiveFig2d
        return InteractiveFig2d(*args, **kwargs)
    else:
        from .static import StaticFig
        return StaticFig(*args, **kwargs)
