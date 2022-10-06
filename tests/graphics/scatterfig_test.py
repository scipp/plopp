# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import scatter_data
from plopp.graphics.scatterfig import ScatterFig
from plopp.graphics.point_cloud import PointCloud
from plopp import input_node
import scipp as sc


def test_creation():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    key = list(fig._children.keys())[0]
    assert isinstance(fig._children[key], PointCloud)
    assert sc.identical(fig._children[key]._data, da)
    assert fig.outline is not None


def test_update():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert len(fig._children) == 1
    key = list(fig._children.keys())[0]
    fig.update(da * 3.3, key=key)
    assert sc.identical(fig._children[key]._data, da * 3.3)


def test_toggle_outline():
    da = scatter_data()
    fig = ScatterFig(input_node(da), x='x', y='y', z='z')
    assert fig.outline.visible
    fig.toggle_outline()
    assert not fig.outline.visible
    fig.toggle_outline()
    assert fig.outline.visible
