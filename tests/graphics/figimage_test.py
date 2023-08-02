# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import pytest
import scipp as sc

from plopp import Node
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
    fig = FigImage(Node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_create_with_bin_edges():
    da = data_array(ndim=2, binedges=True)
    fig = FigImage(Node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_create_with_only_one_bin_edge_coord():
    da = data_array(ndim=2, binedges=True)
    da.coords['xx'] = sc.midpoints(da.coords['xx'])
    fig = FigImage(Node(da))
    assert len(fig.artists) == 1
    assert sc.identical(list(fig.artists.values())[0]._data, da)


def test_log_norm():
    fig = FigImage(norm='log')
    assert fig.colormapper.norm == 'log'


def test_raises_for_new_data_with_incompatible_dimension():
    a = data_array(ndim=2)
    b = a.rename(xx='zz')
    with pytest.raises(sc.DimensionError):
        FigImage(Node(a), Node(b))


def test_raises_for_new_data_with_incompatible_unit():
    a = data_array(ndim=2)
    b = a * a
    with pytest.raises(sc.UnitError):
        FigImage(Node(a), Node(b))


def test_raises_for_new_data_with_incompatible_coord_unit():
    a = data_array(ndim=2)
    b = a.copy()
    b.coords['xx'] = a.coords['xx'] * a.coords['xx']
    with pytest.raises(sc.UnitError):
        FigImage(Node(a), Node(b))


def test_converts_new_data_units():
    a = data_array(ndim=2, unit='m')
    b = data_array(ndim=2, unit='cm')
    anode = Node(a)
    bnode = Node(b)
    fig = FigImage(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    assert sc.identical(fig.artists[bnode.id]._data, b.to(unit='m'))


def test_converts_new_data_coordinate_units():
    a = data_array(ndim=2)
    b = data_array(ndim=2)
    b.coords['xx'].unit = 'cm'
    anode = Node(a)
    bnode = Node(b)
    fig = FigImage(anode, bnode)
    assert sc.identical(fig.artists[anode.id]._data, a)
    c = b.copy()
    c.coords['xx'] = c.coords['xx'].to(unit='m')
    assert sc.identical(fig.artists[bnode.id]._data, c)


def test_colorbar_label_has_correct_unit():
    da = data_array(ndim=2, unit='K')
    fig = FigImage(Node(da))
    assert fig.canvas.cblabel == '[K]'


def test_colorbar_label_has_correct_name():
    da = data_array(ndim=2, unit='K')
    name = 'My Experimental Data'
    da.name = name
    fig = FigImage(Node(da))
    assert fig.canvas.cblabel == name + ' [K]'


def test_colorbar_label_has_no_name_with_multiple_artists():
    a = data_array(ndim=2, unit='K')
    b = 3.3 * a
    a.name = 'A data'
    b.name = 'B data'
    fig = FigImage(Node(a), Node(b))
    assert fig.canvas.cblabel == '[K]'
