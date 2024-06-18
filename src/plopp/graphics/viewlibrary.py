# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from functools import partial

from .. import dispatcher
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


def linefigure(*nodes, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'x': None},
        canvas_maker=dispatcher['canvas'],
        artist_maker=partial(
            dispatcher['line'],
        ),
        colormapper=False,
    )
    return dispatcher['figure'](view_maker, *nodes, **kwargs)


def imagefigure(*nodes, **kwargs) -> FigureLike:
    view_maker = partial(
        GraphicalView,
        dims={'y': None, 'x': None},
        canvas_maker=dispatcher['canvas'],
        artist_maker=partial(
            dispatcher['image'],
        ),
        colormapper=True,
    )
    return dispatcher['figure'](view_maker, *nodes, **kwargs)


# class ViewLibrary:
#     def __getitem__(self, name: str) -> Callable:
#         """
#         Get a module from the backend.
#         """
#         #     module = import_module(f".{name}", __package__)
#         #     return getattr(module, name.capitalize())

#         def figure_func(*nodes, **kwargs) -> FigureLike:
#             # artist_args = {
#             #     key: kwargs.pop(key) for key in ('errorbars', 'mask_color') if key in kwargs
#             # }
#             # # print(kwargs)

#             view_maker = partial(
#                 GraphicalView,
#                 dims={'x': None},
#                 canvas_maker=dispatcher['canvas'],
#                 artist_maker=partial(
#                     dispatcher[name.removesuffix('figure')],  # **artist_args
#                 ),
#                 colormapper=False,
#             )
#             # print(kwargs)
#             return dispatcher['figure'](view_maker, *nodes, **kwargs)

#         return figure_func
