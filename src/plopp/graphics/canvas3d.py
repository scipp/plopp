# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core import View
from .outline import Outline

from copy import copy
import numpy as np
from ipywidgets import VBox


class Canvas3d(View, VBox):

    def __init__(self, figsize=None, title=None):

        import pythreejs as p3

        self.outline = None
        self.axticks = None
        self.figsize = figsize

        if self.figsize is None:
            self.figsize = (600, 400)
        width, height = self.figsize

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

    def make_outline(self, limits):
        if self.outline is not None:
            self.remove(self.outline)
        self.outline = Outline(limits=limits)
        self.add(self.outline)
        self._update_camera(limits=limits)
        self.axes_3d.scale = [self.camera.far] * 3

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

    def add(self, obj):
        self.scene.add(obj)

    def remove(self, obj):
        self.scene.remove(obj)
