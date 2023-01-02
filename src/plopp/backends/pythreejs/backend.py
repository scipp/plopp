# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)


class PythreejsBackend:

    @property
    def is_interactive(self):
        return True

    @property
    def Canvas3d(self):
        from .canvas import Canvas as CanvasP3js
        return CanvasP3js

    @property
    def PointCloud(self):
        from .point_cloud import PointCloud as PointCloudP3js
        return PointCloudP3js

    @property
    def Fig3d(self):
        from .figure import Fig3d as Fig3dP3js
        return Fig3dP3js
