# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class PythreejsBackend:

    def is_interactive(self):
        return True

    def canvas3d(self, *args, **kwargs):
        from .canvas import Canvas as CanvasP3js
        return CanvasP3js(*args, **kwargs)

    def point_cloud(self, *args, **kwargs):
        from .point_cloud import PointCloud as PointCloudP3js
        return PointCloudP3js(*args, **kwargs)

    def figure3d(self, *args, **kwargs):
        from .figure import Fig3d as Fig3dP3js
        return Fig3dP3js(*args, **kwargs)
