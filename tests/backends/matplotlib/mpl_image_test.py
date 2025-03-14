# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array
from plopp.graphics import imagefigure

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


def test_update_on_one_mesh_changes_colors_on_second_mesh():
    da1 = data_array(ndim=2, linspace=False)
    da2 = 3.0 * data_array(ndim=2, linspace=False)
    da2.coords['xx'] += sc.scalar(50.0, unit='m')
    a = Node(da1)
    b = Node(da2)
    f = imagefigure(a, b)
    old_b_colors = f.artists[b.id]._mesh.get_facecolors()
    a.func = lambda: da1 * 2.1
    a.notify_children('updated a')
    f.view.colormapper.autoscale()  # Autoscale the colorbar limits
    # No change because the update did not change the colorbar limits
    assert np.allclose(old_b_colors, f.artists[b.id]._mesh.get_facecolors())
    a.func = lambda: da1 * 5.0
    a.notify_children('updated a')
    f.view.colormapper.autoscale()  # Autoscale the colorbar limits
    assert not np.allclose(old_b_colors, f.artists[b.id]._mesh.get_facecolors())


def test_update_on_one_mesh_changes_colors_on_second_image():
    da1 = data_array(ndim=2, linspace=True)
    da2 = 3.0 * data_array(ndim=2, linspace=True)
    da2.coords['xx'] += sc.scalar(50.0, unit='m')
    a = Node(da1)
    b = Node(da2)
    f = imagefigure(a, b)
    old_b_colors = f.artists[b.id]._image.get_array()
    a.func = lambda: da1 * 2.1
    a.notify_children('updated a')
    f.view.colormapper.autoscale()  # Autoscale the colorbar limits
    # No change because the update did not change the colorbar limits
    assert np.allclose(old_b_colors, f.artists[b.id]._image.get_array())
    a.func = lambda: da1 * 5.0
    a.notify_children('updated a')
    f.view.colormapper.autoscale()  # Autoscale the colorbar limits
    assert not np.allclose(old_b_colors, f.artists[b.id]._image.get_array())


def test_kwargs_are_forwarded_to_artist():
    da = data_array(ndim=2, linspace=False)
    fig = imagefigure(Node(da), rasterized=True)
    [artist] = fig.artists.values()
    assert artist._mesh.get_rasterized()
    fig = imagefigure(Node(da), rasterized=False)
    [artist] = fig.artists.values()
    assert not artist._mesh.get_rasterized()


@pytest.mark.parametrize('linspace', [True, False])
def test_bbox_midpoints(linspace):
    da = data_array(ndim=2, linspace=linspace)
    fig = imagefigure(Node(da))
    [artist] = fig.artists.values()
    bbox = artist.bbox(xscale='linear', yscale='linear')
    assert bbox.xmin < da.coords['xx'].min().value
    assert bbox.xmax > da.coords['xx'].max().value
    assert bbox.ymin < da.coords['yy'].min().value
    assert bbox.ymax > da.coords['yy'].max().value


@pytest.mark.parametrize('linspace', [True, False])
def test_bbox_binedges(linspace):
    da = data_array(ndim=2, binedges=True, linspace=linspace)
    fig = imagefigure(Node(da))
    [artist] = fig.artists.values()
    bbox = artist.bbox(xscale='linear', yscale='linear')
    assert bbox.xmin == da.coords['xx'].min().value
    assert bbox.xmax == da.coords['xx'].max().value
    assert bbox.ymin == da.coords['yy'].min().value
    assert bbox.ymax == da.coords['yy'].max().value
