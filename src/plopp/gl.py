# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import sys

import plopp as _plopp

_plopp.backends['2d'] = 'matplotgl'

sys.modules[__name__] = _plopp
