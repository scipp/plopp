# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)


class PythreejsBackend:

    def is_interactive(self):
        """
        Returns ``True`` if the backend currently in use allows for interactive figures.
        """
        return True

    def canvas3d(self, *args, **kwargs):
        """
        See :class:`canvas.Canvas` for details.
        """
        from .canvas import Canvas as CanvasP3js
        return CanvasP3js(*args, **kwargs)

    def point_cloud(self, *args, **kwargs):
        """
        See :class:`point_cloud.PointCloud` for details.
        """
        from .point_cloud import PointCloud as PointCloudP3js
        return PointCloudP3js(*args, **kwargs)

    def figure3d(self, *args, **kwargs):
        """
        See :class:`figure.Figure` for details.
        """
        from .figure import Figure as FigP3js
        return FigP3js(*args, **kwargs)
