# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

# TODO: Change Sequence to collections.abc.Sequence when we drop support for Python 3.8

from typing import Any, Optional, Sequence, Tuple, Union

import scipp as sc

from ..core.utils import maybe_variable_to_number


def _vector_to_tuple(
    vector: Union[sc.Variable, Sequence[sc.Variable], Sequence[float]]
) -> Tuple[Union[sc.Variable, float], ...]:
    if isinstance(vector, sc.Variable):
        return (vector.fields.x, vector.fields.y, vector.fields.z)
    else:
        return tuple(v for v in vector)


class Camera:
    """
    Camera configuration for three-dimensional plots.
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
        position: Optional[
            Union[sc.Variable, Sequence[sc.Variable], Sequence[float]]
        ] = None,
        look_at: Optional[
            Union[sc.Variable, Sequence[sc.Variable], Sequence[float]]
        ] = None,
        near: Optional[Union[sc.Variable, float]] = None,
        far: Optional[Union[sc.Variable, float]] = None,
    ):
        self._parsed_contents = None
        self._raw_contents = {}
        if position is not None:
            self._raw_contents['position'] = _vector_to_tuple(position)
        if look_at is not None:
            self._raw_contents['look_at'] = _vector_to_tuple(look_at)
        if near is not None:
            self._raw_contents['near'] = near
        if far is not None:
            self._raw_contents['far'] = far

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Attribute getter.
        If units have been set, the value will be converted to the specified units.
        Otherwise, the raw value will be returned.

        Parameters
        ----------
        key:
            The name of the attribute to get.
        default:
            The default value to return if the attribute is not set.
        """
        return (
            self._parsed_contents.get(key, default)
            if self._parsed_contents is not None
            else self._raw_contents.get(key, default)
        )

    def set_units(self, xunit: str, yunit: str, zunit: str):
        """
        Set the units of the camera attributes.
        This will convert the raw values to the specified units.

        Parameters
        ----------
        xunit:
            The unit of the x axis.
        yunit:
            The unit of the y axis.
        zunit:
            The unit of the z axis.
        """
        self._parsed_contents = {}
        for key in set(self._raw_contents) & set(('position', 'look_at')):
            self._parsed_contents[key] = tuple(
                maybe_variable_to_number(x, unit=u)
                for x, u in zip(self._raw_contents[key], [xunit, yunit, zunit])
            )

        for key in set(self._raw_contents) & set(('near', 'far')):
            if isinstance(self._raw_contents[key], sc.Variable):
                if not (xunit == yunit == zunit):
                    raise sc.UnitError(
                        'All axes must have the same unit when specifying a clipping '
                        f'plane with a unit. Units are: {xunit}, {yunit}, {zunit}.'
                    )
            self._parsed_contents[key] = maybe_variable_to_number(
                self._raw_contents[key], unit=xunit
            )

    def has_units(self) -> bool:
        """
        Check if units have been set.
        """
        return self._parsed_contents is not None

    @property
    def position(self) -> Union[Tuple[float, float, float], None]:
        """
        The position of the camera. If camera units have been set, the position returned
        will be converted to the specified units.
        """
        self.get('position')

    @property
    def look_at(self) -> Union[Tuple[float, float, float], None]:
        """
        The point the camera is looking at. If camera units have been set, the position
        returned will be converted to the specified units.
        """
        self.get('look_at')

    @property
    def near(self) -> Union[float, None]:
        """
        The distance to the near clipping plane (how close to the camera objects can be
        before they disappear).
        """
        self.get('near')

    @property
    def far(self) -> Union[float, None]:
        """
        The distance to the far clipping plane (how far from the camera objects can be
        before they disappear).
        """
        self.get('far')

    def __repr__(self):
        return (
            f'Camera(position={self.position}, look_at={self.look_at}, '
            f'near={self.near}, far={self.far})'
        )
