# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.fig3d import Figure3d
from plopp.graphics.point_cloud import PointCloud
from plopp import input_node
import scipp as sc


def test_creation():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    assert isinstance(fig.artists[key], PointCloud)
    assert sc.identical(fig.artists[key]._data, da)


def test_update():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z')
    assert len(fig.artists) == 1
    key = list(fig.artists.keys())[0]
    fig.update(da * 3.3, key=key)
    assert sc.identical(fig.artists[key]._data, da * 3.3)


def test_log_norm():
    da = scatter_data()
    fig = Figure3d(input_node(da), x='x', y='y', z='z', norm='log')
    assert fig.colormapper.norm == 'log'
