# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


class VisibleDeprecationWarning(UserWarning):
    """Visible deprecation warning.

    By default, Python and in particular Jupyter will not show deprecation
    warnings, so this class can be used when a very visible warning is helpful.
    """


VisibleDeprecationWarning.__module__ = 'plopp'
