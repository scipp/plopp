# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import scipp as sc
import numpy as np
from factory import make_dense_data_array, make_dense_dataset
import plopp as pp


def test_plot_ndarray():
    pp.plot(np.arange(50.))._to_widget()


def test_plot_variable():
    pp.plot(sc.arange('x', 50.))._to_widget()


def test_plot_data_array():
    pp.plot(make_dense_data_array(ndim=1))._to_widget()
    da = make_dense_data_array(ndim=2)
    pp.plot(da)._to_widget()


def test_plot_data_array_missing_coords():
    pp.plot(sc.data.table_xyz(100))._to_widget()


def test_plot_dataset():
    ds = make_dense_dataset(ndim=1)
    pp.plot(ds)._to_widget()


def test_plot_dict_of_ndarrays():
    pp.plot({'a': np.arange(50.), 'b': np.arange(60.)})._to_widget()


def test_plot_dict_of_variables():
    pp.plot({'a': sc.arange('x', 50.), 'b': sc.arange('x', 60.)})._to_widget()


def test_plot_dict_of_data_arrays():
    ds = make_dense_dataset(ndim=1)
    pp.plot({'a': ds['a'], 'b': ds['b']})._to_widget()
