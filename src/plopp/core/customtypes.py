# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from collections.abc import Sequence
from typing import Union

from scipp import Variable


class Camera:
    """
    Camera configuration.
    If values are provided as raw numbers instead of Scipp variables, their unit
    will be assumed to be the same as the unit of the spatial coordinates.

    Parameters
    ----------
    position:
        The position of the camera, as a :func:`scipp.vector` or a list of 3 numbers.
    look_at:
        The point the camera is looking at, as a :func:`scipp.vector` or a list of 3
        numbers.
    near:
        The distance to the near clipping plane (how close to the camera objects can be
        before they disappear), as a :func:`scipp.scalar` or a single number.
    far:
        The distance to the far clipping plane (how far from the camera objects can be
        before they disappear), as a :func:`scipp.scalar` or a single number.
    """

    def __init__(
        self,
        position: Union[Variable, Sequence[Variable], Sequence[float]] = None,
        look_at: Union[Variable, Sequence[Variable], Sequence[float]] = None,
        near: Union[Variable, float] = None,
        far: Union[Variable, float] = None,
    ):
        self.position = position
        self.look_at = look_at
        self.near = near
        self.far = far

    def asdict(self):
        out = {}
        for key in ('position', 'look_at', 'near', 'far'):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out
