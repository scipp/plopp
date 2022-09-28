# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import plopp as pp
from plopp.data import scatter_data
import pytest


def test_scatter3d_from_dim():
    da = scatter_data()
    pp.scatter3d(da, dim='position')


def test_scatter3d_from_xyz():
    da = scatter_data()
    pp.scatter3d(da, x='x', y='y', z='z')


def test_scatter3d_raises_with_both_dim_and_xyz():
    da = scatter_data()
    with pytest.raises(ValueError) as e:
        pp.scatter3d(da, dim='position', x='x', y='y', z='z')
    assert str(e.value) == ('If dim (position) is defined, all of '
                            'x (x), y (y), and z (z) must be None.')
