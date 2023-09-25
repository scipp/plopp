# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import pytest

import plopp as pp


def test_creation(use_ipympl):
    da = pp.data.data3d()
    pp.inspector(da)


def test_from_node(use_ipympl):
    da = pp.data.data3d()
    pp.inspector(pp.Node(da))


def test_multiple_inputs_raises(use_ipympl):
    da = pp.data.data3d()
    with pytest.raises(ValueError, match='Cannot convert input of type'):
        pp.inspector({'a': da, 'b': 2.3 * da})


def test_bad_number_of_dims_raises(use_ipympl):
    with pytest.raises(
        ValueError,
        match='The inspector plot currently only works with three-dimensional data',
    ):
        pp.inspector(pp.data.data2d())
    with pytest.raises(
        ValueError,
        match='The inspector plot currently only works with three-dimensional data',
    ):
        pp.inspector(pp.data.data_array(ndim=4))
