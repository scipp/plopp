# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import numpy as np
import plopp as pp
from plopp.data import dense_data_array, dense_dataset
import pytest
import scipp as sc


def test_plot_ndarray():
    pp.plot(np.arange(50.))


def test_plot_variable():
    pp.plot(sc.arange('x', 50.))


def test_plot_data_array():
    pp.plot(dense_data_array(ndim=1))
    da = dense_data_array(ndim=2)
    pp.plot(da)
    pp.plot(da)


def test_plot_data_array_missing_coords():
    da = sc.data.table_xyz(100)
    pp.plot(da)
    assert 'row' not in da.coords


def test_plot_dataset():
    ds = dense_dataset(ndim=1)
    pp.plot(ds)


def test_plot_dict_of_ndarrays():
    pp.plot({'a': np.arange(50.), 'b': np.arange(60.)})


def test_plot_dict_of_variables():
    pp.plot({'a': sc.arange('x', 50.), 'b': sc.arange('x', 60.)})


def test_plot_dict_of_data_arrays():
    ds = dense_dataset(ndim=1)
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
    error_message = "may take very long or use an excessive amount of memory"
    with pytest.raises(ValueError) as e1d:
        pp.plot(np.random.random(1_100_000))
    assert error_message in str(e1d)
    with pytest.raises(ValueError) as e2d:
        pp.plot(np.random.random((3000, 2500)))
    assert error_message in str(e2d)


def test_plot_ignore_size_disables_size_check():
    pp.plot(np.random.random(1_100_000), ignore_size=True)


def test_plot_2d_coord():
    da = dense_data_array(ndim=2, ragged=True)
    pp.plot(da)
    pp.plot(da.transpose())


def test_plot_2d_coord_with_mask():
    da = pp.data.dense_data_array(ndim=2, ragged=True)
    da.masks['negative'] = da.data < sc.scalar(0, unit='m/s')
    pp.plot(da)
