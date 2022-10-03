# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import View
from ..widgets import Toolbar

import scipp as sc
from copy import copy
import numpy as np
from ipywidgets import VBox, HBox


class Scene3d(View, VBox):

    def __init__(self, *nodes, figsize=(600, 400), title=None):

        import pythreejs as p3

        View.__init__(self, *nodes)

        # self._kwargs = kwargs
        self._children = {}
        self.outline = None
        self.axticks = None
        self._figsize = figsize

        width, height = self._figsize

        self.camera = p3.PerspectiveCamera(aspect=width / height)
        self.camera_backup = {}
        self.axes_3d = p3.AxesHelper()
        self.outline = None
        self.scene = p3.Scene(children=[self.camera, self.axes_3d],
                              background="#f0f0f0")
        self.controls = p3.OrbitControls(controlling=self.camera)
        self.renderer = p3.Renderer(camera=self.camera,
                                    scene=self.scene,
                                    controls=[self.controls],
                                    width=width,
                                    height=height)

        self.toolbar = Toolbar(
            tools={
                'home': self.home,
                'camerax': self.camera_x_normal,
                'cameray': self.camera_y_normal,
                'cameraz': self.camera_z_normal,
                'box': self.toggle_outline,
                'axes': self.toggle_axes3d
            })

        self.left_bar = VBox([self.toolbar])
        self.right_bar = VBox()
        self.bottom_bar = HBox()
        self.top_bar = HBox()

        self.render()

        VBox.__init__(self, [
            self.top_bar,
            HBox([self.left_bar, self.renderer, self.right_bar]), self.bottom_bar
        ])

    def _update_camera(self, limits):
        center = [var.mean().value for var in limits]
        distance_from_center = 1.2
        box_size = np.array([(limits[i][1] - limits[i][0]).value for i in range(3)])
        camera_position = list(np.array(center) + distance_from_center * box_size)
        camera_lookat = tuple(center)
        self.camera.position = camera_position
        cam_pos_norm = np.linalg.norm(self.camera.position)
        box_mean_size = np.linalg.norm(box_size)
        self.camera.near = 0.01 * box_mean_size
        self.camera.far = 5.0 * cam_pos_norm
        self.controls.target = camera_lookat
        self.camera.lookAt(camera_lookat)

        # Save camera settings
        self.camera_backup["reset"] = copy(self.camera.position)
        self.camera_backup["center"] = tuple(copy(center))
        self.camera_backup["x_normal"] = [
            center[0] - distance_from_center * box_mean_size, center[1], center[2]
        ]
        self.camera_backup["y_normal"] = [
            center[0], center[1] - distance_from_center * box_mean_size, center[2]
        ]
        self.camera_backup["z_normal"] = [
            center[0], center[1], center[2] - distance_from_center * box_mean_size
        ]

    def notify_view(self, message):
        node_id = message["node_id"]
        new_values = self.graph_nodes[node_id].request_data()
        self.update(new_values=new_values, key=node_id)

    # def update(self, new_values: sc.DataArray, key: str):
    #     """
    #     Update image array with new values.
    #     """
    #     from .point_cloud import PointCloud
    #     from .outline import Outline

    #     if key not in self._children:
    #         pts = PointCloud(data=new_values,
    #                          cbar=self.right_bar,
    #                          figsize=self._figsize,
    #                          **self._kwargs)
    #         self._children[key] = pts
    #         self.scene.add(pts.points)
    #         limits = pts.get_limits()
    #         if self.outline is not None:
    #             self.scene.remove(self.outline)
    #         self.outline = Outline(limits=limits)
    #         self.scene.add(self.outline)
    #         self._update_camera(limits=limits)
    #         self.axes_3d.scale = [self.camera.far] * 3
    #     else:
    #         self._children[key].update(new_values=new_values)

    def render(self):
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id)

    def home(self):
        """
        Reset the camera position.
        """
        self.move_camera(position=self.camera_backup["reset"])

    def camera_x_normal(self):
        """
        View scene along the X normal.
        """
        self.camera_normal(position=self.camera_backup["x_normal"].copy(), ind=0)

    def camera_y_normal(self):
        """
        View scene along the Y normal.
        """
        self.camera_normal(position=self.camera_backup["y_normal"].copy(), ind=1)

    def camera_z_normal(self):
        """
        View scene along the Z normal.
        """
        self.camera_normal(position=self.camera_backup["z_normal"].copy(), ind=2)

    def camera_normal(self, position, ind):
        """
        Move camera to requested normal, and flip if current position is equal
        to the requested position.
        """
        if np.allclose(self.camera.position, position):
            position[ind] = 2.0 * self.camera_backup["center"][ind] - position[ind]
        self.move_camera(position=position)

    def move_camera(self, position):
        self.camera.position = position
        self.controls.target = self.camera_backup["center"]
        self.camera.lookAt(self.camera_backup["center"])

    def toggle_outline(self):
        self.outline.visible = not self.outline.visible

    def toggle_axes3d(self):
        self.axes_3d.visible = not self.axes_3d.visible

    # def get_limits(self):
    #     xmin = None
    #     xmax = None
    #     ymin = None
    #     ymax = None
    #     zmin = None
    #     zmax = None
    #     for child in self._children.values():
    #         xlims, ylims, zlims = child.get_limits()
    #         if xmin is None or xlims[0].value < xmin:
    #             xmin = xlims[0].value
    #         if xmax is None or xlims[1].value > xmax:
    #             xmax = xlims[1].value
    #         if ymin is None or ylims[0].value < ymin:
    #             ymin = ylims[0].value
    #         if ymax is None or ylims[1].value > ymax:
    #             ymax = ylims[1].value
    #         if zmin is None or zlims[0].value < zmin:
    #             zmin = zlims[0].value
    #         if zmax is None or zlims[1].value > zmax:
    #             zmax = zlims[1].value
    #     return (sc.concat([xmin, xmax], dim=self._dims['x']),
    #             sc.concat([ymin, ymax], dim=self._dims['y']))
    #     # return *[
    #     #     reduce(lambda x, y: f(x, y),
    #     #            [child.get_limits()[i][j] for child in self._children.values()])
    #     #     for i in range(3) for j, f in enumerate([min, max])
    #     # ]
