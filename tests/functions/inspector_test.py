# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc
import plopp as pp


@pytest.mark.skip(reason="Requires widget backend")
def test_raises_ValueError_when_given_binned_data():
    da = sc.data.table_xyz(100).bin(x=10, y=20, z=30)
    with pytest.raises(ValueError, match='Cannot plot binned data'):
        pp.inspector(da, orientation='vertical')