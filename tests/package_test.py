# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)
import plopp as pkg


def test_has_version():
    assert hasattr(pkg, '__version__')
