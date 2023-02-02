# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


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

    def is_interactive(self):
        return self._backends['2d'].is_interactive()

    def canvas2d(self, *args, **kwargs):
        try:
            _canvas2d = self._backends['2d'].canvas2d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for canvas2d.')
        return _canvas2d(*args, **kwargs)

    def canvas3d(self, *args, **kwargs):
        try:
            _canvas3d = self._backends['3d'].canvas3d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["3d"]}\' for canvas3d.')
        return _canvas3d(*args, **kwargs)

    def line(self, *args, **kwargs):
        try:
            _line = self._backends['2d'].line
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for line (1D).')
        return _line(*args, **kwargs)

    def image(self, *args, **kwargs):
        try:
            _image = self._backends['2d'].image
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for image (2D).')
        return _image(*args, **kwargs)

    def point_cloud(self, *args, **kwargs):
        try:
            _point_cloud = self._backends['3d'].point_cloud
        except AttributeError:
            raise ValueError(
                f'Unsupported backend \'{self["3d"]}\' for point_cloud (3D).')
        return _point_cloud(*args, **kwargs)

    def figure1d(self, *args, **kwargs):
        try:
            _figure1d = self._backends['2d'].figure1d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for figure1d.')
        return _figure1d(*args, **kwargs)

    def figure2d(self, *args, **kwargs):
        try:
            _figure2d = self._backends['2d'].figure2d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["2d"]}\' for figure2d.')
        return _figure2d(*args, **kwargs)

    def figure3d(self, *args, **kwargs):
        try:
            _figure3d = self._backends['3d'].figure3d
        except AttributeError:
            raise ValueError(f'Unsupported backend \'{self["3d"]}\' for figure3d.')
        return _figure3d(*args, **kwargs)
