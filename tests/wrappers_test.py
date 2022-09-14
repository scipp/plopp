# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import numpy as np
from factory import make_dense_data_array, make_dense_dataset
import plopp as pp
import pytest
import scipp as sc


def test_plot_ndarray():
    pp.plot(np.arange(50.))


def test_plot_variable():
    pp.plot(sc.arange('x', 50.))


def test_plot_data_array():
    pp.plot(make_dense_data_array(ndim=1))
    da = make_dense_data_array(ndim=2)
    pp.plot(da)
    pp.plot(da)


def test_plot_data_array_missing_coords():
    da = sc.data.table_xyz(100)
    pp.plot(da)
    assert 'row' not in da.coords


def test_plot_dataset():
    ds = make_dense_dataset(ndim=1)
    pp.plot(ds)


def test_plot_dict_of_ndarrays():
    pp.plot({'a': np.arange(50.), 'b': np.arange(60.)})


def test_plot_dict_of_variables():
    pp.plot({'a': sc.arange('x', 50.), 'b': sc.arange('x', 60.)})


def test_plot_dict_of_data_arrays():
    ds = make_dense_dataset(ndim=1)
    pp.plot({'a': ds['a'], 'b': ds['b']})


def test_plot_data_array_2d_with_one_missing_coord_and_binedges():
    da = sc.data.table_xyz(100).bin(x=10, y=12).bins.mean()
    del da.coords['x']
    pp.plot(da)


def test_plot_coord_with_no_unit():
    da = sc.data.table_xyz(100).bin(x=10).bins.mean()
    da.coords['x'].unit = None
    pp.plot(da)


def test_plot_rejects_large_input():
    with pytest.raises(ValueError) as e1d:
        pp.plot(np.random.random(2_000_000))
    assert "Attempting to plot data that exceeds reasonable limits" in str(e1d)
    with pytest.raises(ValueError) as e2d:
        pp.plot(np.random.random((6000, 5000)))
    assert "Attempting to plot data that exceeds reasonable limits" in str(e2d)


def test_plot_ignore_size_disables_size_check():
    pp.plot(np.random.random(1_000_001), ignore_size=True)
