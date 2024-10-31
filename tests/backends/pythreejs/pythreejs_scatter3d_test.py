# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp.backends.pythreejs.canvas import Canvas
from plopp.backends.pythreejs.scatter3d import Scatter3d
from plopp.data.testing import scatter


def test_creation():
    da = scatter()
    scat = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z')
    assert sc.identical(scat._data, da)
    assert np.allclose(
        scat.geometry.attributes['position'].array, da.coords['position'].values
    )


def test_update():
    da = scatter()
    scat = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z')
    scat.update(da)
    assert sc.identical(scat._data, da)
    scat.update(da * 2.5)
    assert sc.identical(scat._data, da * 2.5)


def test_bounding_box():
    da = scatter()
    pix = 0.5
    scat = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z', size=pix)
    bbox = scat.bbox(xscale='linear', yscale='linear', zscale='linear')
    assert np.allclose(
        [bbox.xmin, bbox.xmax, bbox.ymin, bbox.ymax, bbox.zmin, bbox.zmax],
        [
            da.coords['x'].min().value - 0.5 * pix,
            da.coords['x'].max().value + 0.5 * pix,
            da.coords['y'].min().value - 0.5 * pix,
            da.coords['y'].max().value + 0.5 * pix,
            da.coords['z'].min().value - 0.5 * pix,
            da.coords['z'].max().value + 0.5 * pix,
        ],
    )


def test_get_limits_flat_panel():
    da = scatter()
    da.coords['z'] *= 0.0
    pix = 0.5
    scat = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z', size=pix)
    bbox = scat.bbox(xscale='linear', yscale='linear', zscale='linear')
    assert np.allclose(
        [bbox.xmin, bbox.xmax, bbox.ymin, bbox.ymax, bbox.zmin, bbox.zmax],
        [
            da.coords['x'].min().value - 0.5 * pix,
            da.coords['x'].max().value + 0.5 * pix,
            da.coords['y'].min().value - 0.5 * pix,
            da.coords['y'].max().value + 0.5 * pix,
            -0.5 * pix,
            0.5 * pix,
        ],
    )


def test_pixel_size():
    """
    We make a reference points cloud because additional factors are potentially added to
    the size, depending on the device pixel ratio. Making a reference with a default
    size of 1 makes it easier to test.
    """
    da = scatter()
    reference = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z', size=1)
    scat = Scatter3d(
        canvas=Canvas(), data=da, x='x', y='y', z='z', size=sc.scalar(2, unit='m')
    )
    assert scat.material.size == 2.0 * reference.material.size


def test_pixel_size_unit_conversion():
    da = scatter()
    reference = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z', size=1)
    scat = Scatter3d(
        canvas=Canvas(), data=da, x='x', y='y', z='z', size=sc.scalar(350, unit='cm')
    )
    assert scat.material.size == 3.5 * reference.material.size
    with pytest.raises(sc.UnitError):
        Scatter3d(
            canvas=Canvas(), data=da, x='x', y='y', z='z', size=sc.scalar(350, unit='s')
        )


def test_pixel_size_cannot_have_units_when_spatial_dimensions_have_different_units():
    da = scatter()
    new_x = da.coords['x'].copy()
    new_x.unit = 's'
    da.coords['x'] = new_x
    reference = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z', size=1)
    with pytest.raises(ValueError, match='The supplied size has unit'):
        Scatter3d(
            canvas=Canvas(), data=da, x='x', y='y', z='z', size=sc.scalar(2.5, unit='m')
        )
    # Ok if no unit supplied
    scat = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z', size=2.5)
    assert scat.material.size == 2.5 * reference.material.size


def test_creation_raises_when_data_is_not_1d():
    da = scatter()
    da2d = sc.broadcast(da, sizes={**da.sizes, **{'time': 10}})
    with pytest.raises(
        sc.DimensionError, match='Scatter3d only accepts data with 1 dimension'
    ):
        Scatter3d(canvas=Canvas(), data=da2d, x='x', y='y', z='z')


def test_update_raises_when_data_is_not_1d():
    da = scatter()
    scat = Scatter3d(canvas=Canvas(), data=da, x='x', y='y', z='z')
    da2d = sc.broadcast(da, sizes={**da.sizes, **{'time': 10}})
    with pytest.raises(
        sc.DimensionError, match='Scatter3d only accepts data with 1 dimension'
    ):
        scat.update(da2d)
