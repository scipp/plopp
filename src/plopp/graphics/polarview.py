# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# from typing import Dict, Literal, Optional, Tuple, Union

# import scipp as sc

from .. import backends
from .lineview import LineView


class PolarView(LineView):
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
