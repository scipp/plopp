# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from copy import copy
from typing import Any, Tuple

import numpy as np
from scipp import Variable


class Canvas:
    """
    WebGL canvas used to render 3D graphics.
    It is based on the ``pythreejs`` library. It provides a scene, camera, controls,
    as well as functions for controlling the camera.
    In addition, it draws a RGB axes helper for the XYZ dimensions, and can draw an
    outline box, given a spatial range in the three directions.

    Parameters
    ----------
    figsize:
        The width and height of the renderer in pixels.
    title:
        The title to be placed above the figure.
    """

    def __init__(self, figsize: Tuple[int, int] = (600, 400), title: str = None):

        # TODO: the title is still unused.

        import pythreejs as p3

        self.xunit = None
        self.yunit = None
        self.zunit = None
        self.outline = None
        self.axticks = None
        self.figsize = figsize
        self.title = title
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

    def to_widget(self):
        return self.renderer

    def make_outline(self, limits: Tuple[Variable, Variable, Variable]):
        """
        Create an outline box with ticklabels, given a range in the XYZ directions.
        """
        from .outline import Outline
        if self.outline is not None:
            self.remove(self.outline)
        self.outline = Outline(limits=limits)
        self.add(self.outline)
        self._update_camera(limits=limits)
        self.axes_3d.scale = [self.camera.far] * 3

    def _update_camera(self, limits: Tuple[Variable, Variable, Variable]):
        """
        Update the camera position when a new object is added to the canvas.
        The camera will look at the mean position of all the objects, and its position
        will be far enough from the center to see all the objects.
        This 'Home' position will be backed up so it can be used when resetting the
        camera via the ``home`` function.
        """
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
        self._camera_normal(position=self.camera_backup["x_normal"].copy(), ind=0)

    def camera_y_normal(self):
        """
        View scene along the Y normal.
        """
        self._camera_normal(position=self.camera_backup["y_normal"].copy(), ind=1)

    def camera_z_normal(self):
        """
        View scene along the Z normal.
        """
        self._camera_normal(position=self.camera_backup["z_normal"].copy(), ind=2)

    def _camera_normal(self, position: Tuple[float, float, float], ind: int):
        """
        Move camera to requested normal, and flip if current position is equal
        to the requested position.
        """
        if np.allclose(self.camera.position, position):
            position[ind] = 2.0 * self.camera_backup["center"][ind] - position[ind]
        self.move_camera(position=position)

    def move_camera(self, position: Tuple[float, float, float]):
        """
        Move the camera to the supplied position.

        Parameters
        ----------
        position:
            The new camera position.
        """
        self.camera.position = position
        self.controls.target = self.camera_backup["center"]
        self.camera.lookAt(self.camera_backup["center"])

    def toggle_outline(self):
        """
        Toggle the visibility of the outline box.
        """
        self.outline.visible = not self.outline.visible

    def toggle_axes3d(self):
        """
        Toggle the visibility of the RGB helper axes.
        """
        self.axes_3d.visible = not self.axes_3d.visible

    def add(self, obj: Any):
        """
        Add an object to the ``scene``.
        """
        self.scene.add(obj)

    def remove(self, obj):
        """
        Remove an object from the ``scene``.
        """
        self.scene.remove(obj)
