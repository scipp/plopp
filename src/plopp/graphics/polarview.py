# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# from typing import Dict, Literal, Optional, Tuple, Union

import scipp as sc

from .. import backends
from .imageview import ImageView
from .lineview import LineView


class PolarLineView(LineView):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **{
                **kwargs,
                **{
                    'artist_maker': backends.polar_line,
                    'canvas_maker': backends.polar_canvas,
                },
            },
        )

    def update(self, new_values: sc.DataArray, key: str):
        """
        Overload of regular update method to ensure that the coordinate is in radians.
        """
        dim = new_values.dim
        if new_values.coords[dim].unit != 'rad':
            new_values.coords[dim] = new_values.coords[dim].to(unit='rad')
        new_values.coords[dim].unit = None
        super().update(new_values, key)


class PolarImageView(ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **{
                **kwargs,
                **{
                    'artist_maker': backends.polar_line,
                    'canvas_maker': backends.polar_canvas,
                },
            },
        )
