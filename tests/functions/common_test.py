# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import plopp as pp
from plopp.data.testing import data_array
from plopp.functions.common import preprocess
import pytest
import scipp as sc


def test_preprocess_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        preprocess(da)


def test_preprocess_use_non_dimension_coords():
    da = data_array(ndim=2)
    da.coords['xx2'] = 7.5 * da.coords['xx']
    da.coords['yy2'] = 3.3 * da.coords['yy']
    out = preprocess(da, coords=['xx2', 'yy2'])
    assert set(out.dims) == {'xx2', 'yy2'}
    assert out.coords['xx2'].max() == 7.5 * da.coords['xx'].max()
    assert out.coords['yy2'].max() == 3.3 * da.coords['yy'].max()


def test_preprocess_warns_when_coordinate_is_not_sorted():
    da = pp.data.data_array(ndim=1)
    unsorted = sc.concat([da['x', 20:], da['x', :20]], dim='x')
    with pytest.warns(UserWarning,
                      match='The input contains a coordinate with unsorted values'):
        preprocess(unsorted)
