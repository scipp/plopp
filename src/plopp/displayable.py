# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class Displayable:

    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        Mimebundle display representation for jupyter notebooks.
        """
        return self.to_widget()._repr_mimebundle_(include=include, exclude=exclude)
