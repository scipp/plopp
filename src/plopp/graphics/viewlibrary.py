# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Callable
from functools import partial

from .. import backends, dispatcher
from ..core.typing import FigureLike
from .graphicalview import GraphicalView


class ViewLibrary:
    def __getitem__(self, name: str) -> Callable:
        """
        Get a module from the backend.
        """
        #     module = import_module(f".{name}", __package__)
        #     return getattr(module, name.capitalize())

        def figure_func(*nodes, **kwargs) -> FigureLike:
            # artist_args = {
            #     key: kwargs.pop(key) for key in ('errorbars', 'mask_color') if key in kwargs
            # }
            # # print(kwargs)

            view_maker = partial(
                GraphicalView,
                dims={'x': None},
                canvas_maker=dispatcher['canvas'],
                artist_maker=partial(
                    dispatcher['line'.removesuffix('figure')],  # **artist_args
                ),
                colormapper=False,
            )
            # print(kwargs)
            return dispatcher['figure'](view_maker, *nodes, **kwargs)

        return figure_func
