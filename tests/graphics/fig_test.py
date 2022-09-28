# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.fig import Figure
from plopp.graphics.line import Line
from plopp.graphics.mesh import Mesh
from plopp import input_node
import scipp as sc
from common import make_axes
import pytest


def test_figure_creation():
    title = 'My Figure'
    fig = Figure(ax=make_axes(), title=title)
    assert fig._ax.get_title() == title
    assert fig._ax.get_xscale() == 'linear'
    assert fig._ax.get_yscale() == 'linear'


def test_figure_logx():
    fig = Figure(ax=make_axes())
    assert fig._ax.get_xscale() == 'linear'
    fig.logx()
    assert fig._ax.get_xscale() == 'log'
    fig.logx()
    assert fig._ax.get_xscale() == 'linear'


def test_figure_logy():
    fig = Figure(ax=make_axes())
    assert fig._ax.get_yscale() == 'linear'
    fig.logy()
    assert fig._ax.get_yscale() == 'log'
    fig.logy()
    assert fig._ax.get_yscale() == 'linear'


def test_fig_update_1d():
    fig = Figure(ax=make_axes())
    assert len(fig._children) == 0
    da = dense_data_array(ndim=1)
    key = 'data1d'
    fig.update(da, key=key)
    assert isinstance(fig._children[key], Line)
    assert sc.identical(fig._children[key]._data, da)


def test_fig_update_2d():
    fig = Figure(ax=make_axes())
    assert len(fig._children) == 0
    da = dense_data_array(ndim=2)
    key = 'data2d'
    fig.update(da, key=key)
    assert isinstance(fig._children[key], Mesh)
    assert sc.identical(fig._children[key]._data, da)


def test_fig_update_3d_raises():
    fig = Figure(ax=make_axes())
    da = dense_data_array(ndim=3)
    key = 'data3d'
    with pytest.raises(ValueError) as e:
        fig.update(da, key=key)
    assert str(e.value) == "Figure can only be used to plot 1-D and 2-D data."


def test_fig_create_with_node():
    da = dense_data_array(ndim=1)
    fig = Figure(input_node(da), ax=make_axes())
    assert len(fig._children) == 1
    assert sc.identical(list(fig._children.values())[0]._data, da)


def test_figure_crop():
    fig = Figure(ax=make_axes())
    da = dense_data_array(ndim=2, binedges=True)
    key = 'data2d'
    fig.update(da, key=key)
    fig._autoscale()
    assert fig._ax.get_xlim() == (da.meta['xx'].min().value, da.meta['xx'].max().value)
    assert fig._ax.get_ylim() == (da.meta['yy'].min().value, da.meta['yy'].max().value)
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    ymin = sc.scalar(5.5, unit='m')
    ymax = sc.scalar(22.3, unit='m')
    fig.crop(xx={'min': xmin, 'max': xmax}, yy={'min': ymin, 'max': ymax})
    assert fig._ax.get_xlim() == (xmin.value, xmax.value)
    assert fig._ax.get_ylim() == (ymin.value, ymax.value)
