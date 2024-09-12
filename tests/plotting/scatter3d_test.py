# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import tempfile

import numpy as np
import pytest
import scipp as sc

import plopp as pp
from plopp.data.testing import data_array, scatter


def test_scatter3d_from_pos():
    da = scatter()
    pp.scatter3d(da, pos='position')


def test_scatter3d_from_xyz():
    da = scatter()
    pp.scatter3d(da, x='x', y='y', z='z')


def test_scatter3d_from_xyz_using_defaults():
    da = scatter()
    pp.scatter3d(da)


def test_scatter3d_dimensions_are_flattened():
    nx = 12
    ny = 12
    x = sc.linspace(dim='x', start=-10.0, stop=10.0, num=nx, unit='m')
    y = sc.linspace(dim='y', start=-10.0, stop=10.0, num=ny, unit='m')
    da = sc.DataArray(
        data=sc.array(dims=['x', 'y'], values=np.random.rand(nx, ny)),
        coords={'position': sc.spatial.as_vectors(x, y, 0.0 * sc.units.m)},
    )
    p = pp.scatter3d(da, pos="position")
    assert next(iter(p.artists.values())).data.ndim == 1
    nz = 12
    z = sc.linspace(dim='z', start=-10.0, stop=10.0, num=nz, unit='m')
    da = sc.DataArray(
        data=sc.array(dims=['x', 'y', 'z'], values=np.random.rand(nx, ny, nz)),
        coords={'position': sc.spatial.as_vectors(x, y, z)},
    )
    p = pp.scatter3d(da, pos="position")
    assert next(iter(p.artists.values())).data.ndim == 1


def test_scatter3d_can_plot_scalar_data():
    da = sc.DataArray(
        data=sc.scalar(1.2), coords={'position': sc.vector(value=[1, 2, 3])}
    )
    p = pp.scatter3d(da, pos='position')
    assert next(iter(p.artists.values())).data.ndim == 1


def test_raises_ValueError_when_given_binned_data():
    nx = 10
    da = sc.data.table_xyz(100).bin(x=nx)
    x = sc.linspace(dim='x', start=-10.0, stop=10.0, num=nx, unit='m')
    da.coords['position'] = sc.spatial.as_vectors(x, x, x)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.scatter3d(da, pos='position')


def test_raises_ValueError_when_given_ax_kwarg():
    da = scatter()
    with pytest.raises(ValueError, match='Keyword "ax" detected'):
        pp.scatter3d(da, x='x', y='y', z='z', ax='dummy')


def test_scatter3d_from_xarray():
    import xarray as xr

    N = 200
    data = np.random.random(N)
    x = np.random.normal(size=N)
    y = np.random.normal(size=N)
    z = np.random.normal(size=N)
    da = xr.DataArray(
        data,
        coords={'x': ('pixel', x), 'y': ('pixel', y), 'z': ('pixel', z)},
        dims=['pixel'],
    )
    pp.scatter3d(da, x='x', y='y', z='z')


def test_scatter3d_dict_of_inputs():
    da1 = scatter()
    da2 = scatter()
    da2.coords['x'] += sc.scalar(100, unit='m')
    fig = pp.scatter3d({'a': da1, 'b': da2})
    assert len(fig.artists) == 2


def test_scatter3d_from_node():
    pp.scatter3d(pp.Node(scatter()))


def test_scatter3d_from_multiple_nodes():
    a = scatter()
    b = scatter()
    b.coords['x'] += sc.scalar(100, unit='m')
    pp.scatter3d({'a': pp.Node(a), 'b': pp.Node(b)})


def test_scatter3d_mixing_raw_data_and_nodes():
    a = scatter()
    b = scatter()
    b.coords['x'] += sc.scalar(100, unit='m')
    pp.scatter3d({'a': a, 'b': pp.Node(b)})
    pp.scatter3d({'a': pp.Node(a), 'b': b})


def test_save_to_html():
    fig = pp.scatter3d(scatter())
    with tempfile.TemporaryDirectory() as path:
        fname = os.path.join(path, 'plopp_fig3d.html')
        fig.save(filename=fname)
        assert os.path.isfile(fname)


def test_save_to_html_with_bad_extension_raises():
    fig = pp.scatter3d(scatter())
    with pytest.raises(ValueError, match=r'File extension must be \.html'):
        fig.save(filename='plopp_fig3d.png')


def test_scatter3d_does_not_accept_data_with_other_dimensionality_on_update():
    da = scatter()
    fig = pp.scatter3d(da)
    # There is no 'z' coordinate in the data
    with pytest.raises(KeyError, match='Supplied data is incompatible with this view'):
        fig.update(new=data_array(ndim=2, dim_list="xyzab"))
    # The data has 3 dimensions
    with pytest.raises(
        sc.DimensionError, match='Scatter3d only accepts data with 1 dimension'
    ):
        fig.update(new=data_array(ndim=3, dim_list="xyzab"))


def test_figure_has_data_name_on_colorbar_for_one_set_of_scatter_points():
    da = scatter()
    da.name = "MyScatterData"
    fig = pp.scatter3d(da, cbar=True)
    ylabel = fig.view.colormapper.ylabel
    assert da.name in ylabel
    assert str(da.unit) in ylabel


def test_figure_has_only_unit_on_colorbar_for_multiple_sets_of_scatter_points():
    a = scatter(seed=1)
    a.name = "A data"
    b = scatter(seed=2)
    b.name = "B data"
    fig = pp.scatter3d({'a': a, 'b': b}, cbar=True)
    ylabel = fig.view.colormapper.ylabel
    assert str(a.unit) in ylabel
    assert str(b.unit) in ylabel
    assert a.name not in ylabel
    assert b.name not in ylabel
