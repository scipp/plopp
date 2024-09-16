# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import functools
import warnings
from collections.abc import Callable

from .core.typing import VisibleDeprecationWarning
from .graphics.basefig import BaseFig


def deprecated(message: str = '') -> Callable:
    def decorator(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f'{function.__name__} is deprecated. {message}',
                VisibleDeprecationWarning,
                stacklevel=2,
            )
            return function(*args, **kwargs)

        return wrapper

    return decorator


def to_dict(fig: BaseFig) -> dict:
    """
    Convert a figure to a dictionary.
    The output should contain all the information necessary to re-create the figure.

    Parameters
    ----------
    fig:
        The figure to convert.
    """
    canvas = fig.canvas
    view = fig.view
    out = {"axes": {}, "artists": {}, "title": canvas.title}
    axes = "xy"
    if hasattr(canvas, "zrange"):
        axes += "z"
    for c in axes:
        out["axes"][c] = {
            attr: getattr(canvas, f"{c}{attr}") for attr in ("label", "range")
        }
    for key, artist in view.artists.items():
        out["artists"][key] = artist.to_dict()
        if out["artists"][key]["type"] in ("heatmap", "scatter"):
            out["artists"][key]["colorscale"] = fig.view.colormapper.to_dict()
    return out


__all__ = ['deprecated', 'to_dict']
