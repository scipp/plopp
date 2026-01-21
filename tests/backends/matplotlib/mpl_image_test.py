# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib as mpl
import numpy as np
import pytest
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array
from plopp.graphics import imagefigure

pytestmark = pytest.mark.usefixtures("_parametrize_mpl_backends")


@pytest.mark.parametrize('linspace', [True, False])
def test_update_on_one_image_changes_colors_on_second_image(linspace):
    da1 = data_array(ndim=2, linspace=linspace)
    da2 = 3.0 * data_array(ndim=2, linspace=linspace)
    da2.coords['xx'] += sc.scalar(50.0, unit='m')
    a = Node(da1)
    b = Node(da2)
    f = imagefigure(a, b)
    old_b_colors = getattr(
        f.artists[b.id]._image, "get_array" if linspace else "get_facecolors"
    )()
    a.func = lambda: da1 * 2.1
    a.notify_children('updated a')
    f.view.colormapper.autoscale()  # Autoscale the colorbar limits
    # No change because the update did not change the colorbar limits
    # colors = f.artists[b.id]._image.get_array() if linspace else
    assert np.allclose(
        old_b_colors,
        getattr(
            f.artists[b.id]._image, "get_array" if linspace else "get_facecolors"
        )(),
    )
    a.func = lambda: da1 * 5.0
    a.notify_children('updated a')
    f.view.colormapper.autoscale()  # Autoscale the colorbar limits
    assert not np.allclose(
        old_b_colors,
        getattr(
            f.artists[b.id]._image, "get_array" if linspace else "get_facecolors"
        )(),
    )


def test_kwargs_are_forwarded_to_artist():
    da = data_array(ndim=2, linspace=False)
    fig = imagefigure(Node(da), rasterized=True)
    [artist] = fig.artists.values()
    assert artist._image.get_rasterized()
    fig = imagefigure(Node(da), rasterized=False)
    [artist] = fig.artists.values()
    assert not artist._image.get_rasterized()


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


def test_pass_mpl_cmap_object():
    da = data_array(ndim=2)
    cmap = mpl.colormaps['plasma']
    imagefigure(Node(da), cmap=cmap)
