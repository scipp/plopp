# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import scipp as sc

from plopp import Node
from plopp.data.testing import data_array
from plopp.graphics import imagefigure


def test_update_on_one_mesh_changes_colors_on_second_mesh():
    da1 = data_array(ndim=2)
    da2 = 3.0 * data_array(ndim=2)
    da2.coords['xx'] += sc.scalar(50.0, unit='m')
    a = Node(da1)
    b = Node(da2)
    f = imagefigure(a, b)
    old_b_colors = f.artists[b.id]._mesh.get_facecolors()
    a.func = lambda: da1 * 2.1
    a.notify_children('updated a')
    # No change because the update did not change the colorbar limits
    assert np.allclose(old_b_colors, f.artists[b.id]._mesh.get_facecolors())
    a.func = lambda: da1 * 5.0
    a.notify_children('updated a')
    assert not np.allclose(old_b_colors, f.artists[b.id]._mesh.get_facecolors())


def test_with_string_coord():
    strings = ['a', 'b', 'c', 'd', 'e']
    da = sc.DataArray(
        data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
        coords={
            'x': sc.array(dims=['x'], values=strings, unit='s'),
            'y': sc.arange('y', 5.0, unit='m'),
        },
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(
        data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
        coords={
            'x': sc.array(dims=['x'], values=strings, unit='s'),
            'y': sc.arange('y', 6.0, unit='m'),
        },
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_with_strings_as_bin_edges_other_coord_is_bin_centers():
    strings = ['a', 'b', 'c', 'd', 'e', 'f']
    da = sc.DataArray(
        data=sc.array(dims=['y', 'x'], values=np.random.random((5, 5))),
        coords={
            'x': sc.array(dims=['x'], values=strings, unit='s'),
            'y': sc.arange('y', 5.0, unit='m'),
        },
    )
    fig = da.plot()
    assert [t.get_text() for t in fig.canvas.ax.get_xticklabels()] == strings


def test_kwargs_are_forwarded_to_artist():
    da = data_array(ndim=2)
    fig = da.plot(rasterized=True)
    [artist] = fig.artists.values()
    assert artist._mesh.get_rasterized()
    fig = da.plot(rasterized=False)
    [artist] = fig.artists.values()
    assert not artist._mesh.get_rasterized()
