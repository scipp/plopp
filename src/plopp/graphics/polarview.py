# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


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


class PolarImageView(ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **{
                **kwargs,
                **{
                    'artist_maker': backends.polar_image,
                    'canvas_maker': backends.polar_canvas,
                },
            },
        )
