# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class BackendManager:

    def __init__(self):
        self._mapping = {'2d': 'matplotlib', '3d': 'pythreejs'}
        self._backends = {}
        self._sync()

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        self._mapping[key] = value
        self._sync()

    def keys(self):
        return self._mapping.keys()

    def values(self):
        return self._mapping.values()

    def items(self):
        return self._mapping.items()

    def _sync(self):
        if self._mapping['2d'] == 'matplotlib':
            from .matplotlib import MatplotlibBackend
            self._backends['2d'] = MatplotlibBackend()
        elif self._mapping['2d'] == 'plotly':
            from .plotly import PlotlyBackend
            self._backends['2d'] = PlotlyBackend()
        else:
            raise ValueError(f'Unsupported 2d backend \'{self._mapping["2d"]}\'.')

        if self._mapping['3d'] == 'pythreejs':
            from .pythreejs import PythreejsBackend
            self._backends['3d'] = PythreejsBackend()
        else:
            raise ValueError(f'Unsupported 3d backend \'{self._mapping["3d"]}\'.')

    @property
    def is_interactive(self):
        return self._backends['2d'].is_interactive

    @property
    def Canvas2d(self):
        try:
            return self._backends['2d'].Canvas2d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for Canvas2d.')

    @property
    def Canvas3d(self):
        try:
            return self._backends['3d'].Canvas3d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["3d"]}\' for Canvas3d.')

    @property
    def Line(self):
        try:
            return self._backends['2d'].Line
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for Line (1D).')

    @property
    def Image(self):
        try:
            return self._backends['2d'].Image
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for Image (2D).')

    @property
    def PointCloud(self):
        try:
            return self._backends['3d'].PointCloud
        except AttributeError:
            raise ValueError(
                f'Unsupported backend \'{self["3d"]}\' for PointCloud (3D).')

    @property
    def Fig1d(self):
        try:
            return self._backends['2d'].Fig1d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for Fig1d.')

    @property
    def Fig2d(self):
        try:
            return self._backends['2d'].Fig2d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for Fig2d.')

    @property
    def Fig3d(self):
        try:
            return self._backends['3d'].Fig3d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["3d"]}\' for Fig3d.')
