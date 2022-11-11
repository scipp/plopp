# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import numpy as np
import plopp as pp
from plopp.data import scatter_data
import pytest
import scipp as sc


def test_scatter3d_from_pos():
    da = scatter_data()
    pp.scatter3d(da, pos='position')


def test_scatter3d_from_xyz():
    da = scatter_data()
    pp.scatter3d(da, x='x', y='y', z='z')


def test_scatter3d_raises_with_both_pos_and_xyz():
    da = scatter_data()
    with pytest.raises(ValueError) as e:
        pp.scatter3d(da, pos='position', x='x', y='y', z='z')
    assert str(e.value) == ('If pos (position) is defined, all of '
                            'x (x), y (y), and z (z) must be None.')


def test_scatter3d_dimensions_are_flattened():
    nx = 12
    ny = 12
    x = sc.linspace(dim='x', start=-10.0, stop=10.0, num=nx, unit='m')
    y = sc.linspace(dim='y', start=-10.0, stop=10.0, num=ny, unit='m')
    da = sc.DataArray(data=sc.array(dims=['x', 'y'], values=np.random.rand(nx, ny)),
                      coords={'position': sc.geometry.position(x, y, 0.0 * sc.units.m)})
    p = pp.scatter3d(da, pos="position")
    assert list(p.children[0].artists.values())[0].data.ndim == 1
    nz = 12
    z = sc.linspace(dim='z', start=-10.0, stop=10.0, num=nz, unit='m')
    da = sc.DataArray(data=sc.array(dims=['x', 'y', 'z'],
                                    values=np.random.rand(nx, ny, nz)),
                      coords={'position': sc.geometry.position(x, y, z)})
    p = pp.scatter3d(da, pos="position")
    assert list(p.children[0].artists.values())[0].data.ndim == 1
