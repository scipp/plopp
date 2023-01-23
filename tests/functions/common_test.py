# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import numpy as np
import pytest
import scipp as sc

from plopp.data.testing import data_array
from plopp.functions.common import preprocess


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
    da = data_array(ndim=1)
    unsorted = sc.concat([da['xx', 20:], da['xx', :20]], dim='xx')
    with pytest.warns(UserWarning,
                      match='The input contains a coordinate with unsorted values'):
        preprocess(unsorted)


def test_preprocess_no_warning_if_dtype_cannot_be_sorted():
    da = data_array(ndim=1)
    da.coords['vecs'] = sc.vectors(dims=['xx'],
                                   values=np.random.random((da.sizes['xx'], 3)))
    out = preprocess(da)  # no warning should be emitted
    assert 'vecs' in out.coords
    da.coords['strings'] = sc.array(dims=['xx'],
                                    values=list('ba' * (da.sizes['xx'] // 2)))
    out = preprocess(da)  # no warning should be emitted
    assert 'strings' in out.coords
