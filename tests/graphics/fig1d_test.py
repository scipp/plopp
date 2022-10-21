# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from plopp.data import dense_data_array
from plopp.graphics.fig1d import Figure1d
from plopp.graphics.line import Line
from plopp import input_node
import scipp as sc
import pytest


def test_empty():
    fig = Figure1d()
    assert len(fig.artists) == 0


def test_update():
    fig = Figure1d()
    assert len(fig.artists) == 0
    da = dense_data_array(ndim=1)
    key = 'data1d'
    fig.update(da, key=key)
    assert isinstance(fig.artists[key], Line)
    assert sc.identical(fig.artists[key]._data, da)


def test_update_not_1d_raises():
    fig = Figure1d()
    with pytest.raises(ValueError) as e:
        fig.update(dense_data_array(ndim=2), key='data2d')
    assert str(e.value) == "Figure1d can only be used to plot 1-D data."
    with pytest.raises(ValueError) as e:
        fig.update(dense_data_array(ndim=3), key='data3d')
    assert str(e.value) == "Figure1d can only be used to plot 1-D data."


def test_create_with_node():
    da = dense_data_array(ndim=1)
    fig = Figure1d(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_log_norm():
    fig = Figure1d()
    assert fig.canvas.yscale == 'linear'
    fig = Figure1d(norm='log')
    assert fig.canvas.yscale == 'log'


def test_crop():
    da = dense_data_array(ndim=1)
    fig = Figure1d(input_node(da))
    assert fig.canvas.ax.get_xlim()[0] < da.meta['xx'].min().value
    assert fig.canvas.ax.get_xlim()[1] > da.meta['xx'].max().value
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    fig.crop(xx={'min': xmin, 'max': xmax})
    assert fig.canvas.ax.get_xlim() == (xmin.value, xmax.value)
    with pytest.raises(KeyError):
        fig.crop(yy={'min': xmin, 'max': xmax})


def test_update_grows_limits():
    da = dense_data_array(ndim=1)
    fig = Figure1d(input_node(da))
    old_lims = fig.canvas.ax.get_ylim()
    key = list(fig.artists.keys())[0]
    fig.update(da * 2.5, key=key)
    new_lims = fig.canvas.ax.get_ylim()
    assert new_lims[0] < old_lims[0]
    assert new_lims[1] > old_lims[1]


def test_update_does_not_shrink_limits():
    da = dense_data_array(ndim=1)
    fig = Figure1d(input_node(da))
    old_lims = fig.canvas.ax.get_ylim()
    key = list(fig.artists.keys())[0]
    fig.update(da * 0.5, key=key)
    new_lims = fig.canvas.ax.get_ylim()
    assert new_lims[0] == old_lims[0]
    assert new_lims[1] == old_lims[1]
