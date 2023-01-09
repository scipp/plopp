# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import plopp as pp


def test_plot_data_array_1d():
    pp.plot(pp.data.data_array(ndim=1))


def test_plot_data_array_2d():
    pp.plot(pp.data.data_array(ndim=2))
