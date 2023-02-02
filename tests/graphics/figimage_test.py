# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

from plopp import input_node
from plopp.data.testing import data_array
from plopp.graphics.figimage import FigImage


def test_empty():
    fig = FigImage()
    assert len(fig.artists) == 0


def test_update():
    fig = FigImage()
    assert len(fig.artists) == 0
    da = data_array(ndim=2)
    key = 'data2d'
    fig.update(da, key=key)
    assert sc.identical(fig.artists[key]._data, da)


def test_update_not_2d_raises():
    fig = FigImage()
    with pytest.raises(ValueError, match="FigImage can only be used to plot 2-D data."):
        fig.update(data_array(ndim=1), key='data1d')
    with pytest.raises(ValueError, match="FigImage can only be used to plot 2-D data."):
        fig.update(data_array(ndim=3), key='data3d')


def test_create_with_node():
    da = data_array(ndim=2)
    fig = FigImage(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_create_with_bin_edges():
    da = data_array(ndim=2, binedges=True)
    fig = FigImage(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_create_with_only_one_bin_edge_coord():
    da = data_array(ndim=2, binedges=True)
    da.coords['xx'] = sc.midpoints(da.coords['xx'])
    fig = FigImage(input_node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_log_norm():
    fig = FigImage(norm='log')
    assert fig.colormapper.norm == 'log'


def test_crop():
    da = data_array(ndim=2, binedges=True)
    fig = FigImage(input_node(da))
    assert fig.canvas.xrange == (da.meta['xx'].min().value, da.meta['xx'].max().value)
    assert fig.canvas.yrange == (da.meta['yy'].min().value, da.meta['yy'].max().value)
    xmin = sc.scalar(2.1, unit='m')
    xmax = sc.scalar(102.0, unit='m')
    ymin = sc.scalar(5.5, unit='m')
    ymax = sc.scalar(22.3, unit='m')
    fig.crop(xx={'min': xmin, 'max': xmax}, yy={'min': ymin, 'max': ymax})
    assert fig.canvas.xrange == (xmin.value, xmax.value)
    assert fig.canvas.yrange == (ymin.value, ymax.value)


def test_crop_no_variable():
    da = data_array(ndim=2)
    xmin = 2.1
    xmax = 102.0
    ymin = 5.5
    ymax = 22.3
    fig = FigImage(input_node(da),
                   crop={
                       'xx': {
                           'min': xmin,
                           'max': xmax
                       },
                       'yy': {
                           'min': ymin,
                           'max': ymax
                       }
                   })
    assert fig.canvas.xrange == (xmin, xmax)
    assert fig.canvas.yrange == (ymin, ymax)


def test_raises_for_new_data_with_incompatible_dimension():
    a = data_array(ndim=2)
    b = a.rename(xx='zz')
    with pytest.raises(sc.DimensionError):
        FigImage(input_node(a), input_node(b))


def test_raises_for_new_data_with_incompatible_unit():
    a = data_array(ndim=2)
    b = a * a
    with pytest.raises(sc.UnitError):
        FigImage(input_node(a), input_node(b))


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = data_array(ndim=2)
    b = a.copy()
    b.coords['xx'] = a.coords['xx'] * a.coords['xx']
    with pytest.raises(sc.UnitError):
        FigImage(input_node(a), input_node(b))


def test_converts_new_data_units():
    a = data_array(ndim=2, unit='m')
    b = data_array(ndim=2, unit='cm')
    anode = input_node(a)
    bnode = input_node(b)
    fig = FigImage(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = data_array(ndim=2)
    b = data_array(ndim=2)
    b.coords['xx'].unit = 'cm'
    anode = input_node(a)
    bnode = input_node(b)
    fig = FigImage(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['xx'] = c.coords['xx'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)
