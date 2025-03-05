# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Scipp contributors (https://github.com/scipp)

"""Tests of package integrity.

Note that additional imports need to be added for repositories that
contain multiple packages.
"""

import plopp as pkg


def test_has_version():
    assert hasattr(pkg, '__version__')


# This is for CI package tests. They need to run tests with minimal dependencies,
# that is, without installing pytest. This code does not affect pytest.
if __name__ == '__main__':
    test_has_version()
