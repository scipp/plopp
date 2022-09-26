# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.utils import number_to_variable, name_with_unit
from ..core import View
from ..widgets import Toolbar
from .io import fig_to_bytes
from .point_cloud import PointCloud
from .outline import Outline

import scipp as sc
from typing import Any, Tuple
from copy import copy

# import ipywidgets as ipw
import matplotlib.pyplot as plt
import numpy as np
from typing import Any, Tuple
# import pythreejs as p3

from ipywidgets import VBox, HBox


class Scene3d(View, VBox):

    def __init__(self, *nodes, figsize=(800, 500), title=None, **kwargs):

        import pythreejs as p3

        # super().__init__(*nodes)
        View.__init__(self, *nodes)

        # self._dim = dim
        self._kwargs = kwargs
        self._children = {}
        self.outline = None
        self.axticks = None

        width, height = figsize

        self.camera = p3.PerspectiveCamera(position=[20, 0, 0], aspect=width / height)
        self.camera_backup = {}

        # Add red/green/blue axes helper
        self.axes_3d = p3.AxesHelper()

        self.outline = None

        # Create the pythreejs scene
        self.scene = p3.Scene(children=[self.camera, self.axes_3d],
                              background="#f0f0f0")

        # Add camera controller
        # TODO: additional parameters whose default values are Inf need to be specified
        # here to avoid a warning being raised: minAzimuthAngle, maxAzimuthAngle,
        # maxDistance, maxZoom. Note that we change the maxDistance once we know the
        # extents of the box.
        # See https://github.com/jupyter-widgets/pythreejs/issues/366.
        self.controls = p3.OrbitControls(controlling=self.camera)
        # ,
        #                                  minAzimuthAngle=-1.0e9,
        #                                  maxAzimuthAngle=1.0e9,
        #                                  maxDistance=100.0,
        #                                  maxZoom=0.01)

        # Render the scene into a widget
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

    # def _ipython_display_(self):
    #     """
    #     IPython display representation for Jupyter notebooks.
    #     """
    #     return self._to_widget()._ipython_display_()

    # def _to_widget(self):
    #     """
    #     Return the renderer and the colorbar into a widget box.
    #     """
    #     self.render()
    #     return self.renderer

    def _update_camera(self, limits):
        # Set camera controller target
        center = [var.mean().value for var in limits]
        distance_from_center = 1.2
        box_size = np.array([(limits[i][1] - limits[i][0]).value for i in range(3)])
        camera_position = list(np.array(center) + distance_from_center * box_size)
        camera_lookat = tuple(center)
        # if self.initial_camera_view is not None:
        #     camera_position = self.initial_camera_view.get('position', camera_position)
        #     camera_lookat = tuple(self.initial_camera_view.get(
        #         'look_at', camera_lookat))
        #     self.initial_camera_view = None
        self.camera.position = camera_position
        cam_pos_norm = np.linalg.norm(self.camera.position)
        box_mean_size = np.linalg.norm(box_size)
        self.camera.near = 0.01 * box_mean_size
        self.camera.far = 5.0 * cam_pos_norm
        self.controls.target = camera_lookat
        self.camera.lookAt(camera_lookat)
        # TODO: Update OrbitControls maxDistance. This should be removed once
        # https://github.com/jupyter-widgets/pythreejs/issues/366 is resolved.
        # self.controls.maxDistance = self.camera.far * 5.0

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

    def update(self, new_values: sc.DataArray, key: str):
        """
        Update image array with new values.
        """
        if key not in self._children:
            # self._new_artist = True
            # print(self._kwargs)
            pts = PointCloud(data=new_values, cbar=self.right_bar, **self._kwargs)
            self._children[key] = pts
            self.scene.add(pts.points)
            limits = pts.get_limits()
            # center = sc.concat(limits, dim='x').fold('x', sizes={
            #     'x': 3,
            #     'y': 2
            # }).mean('y')
            if self.outline is not None:
                self.scene.remove(self.outline)
            # self.outline.update(limits=limits)
            self.outline = Outline(limits=limits)
            self.scene.add(self.outline)
            self._update_camera(limits=limits)
            self.axes_3d.scale = [self.camera.far] * 3
            # self.scene.add(self.outline.all)
            # self.right_bar.children = list(self.right_bar.children) + [pts.colorbar]

            # self.camera.add(self._children[key].cbar)
            # self.camera.near = 0.01
            # self._children[key].cbar.position = [0.6, 0, -1]
            # self.renderer.controls = self.renderer.controls + [
            #     self._children[key].click_picker
            # ]
        else:
            self._children[key].update(new_values=new_values)

    def render(self):
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id)

    # def _make_outline(self, limits, center):
    #     """
    #     Make a wireframe cube with tick labels
    #     """
    #     box_geometry = p3.BoxBufferGeometry(width=(limits[1] - limits[0]).value,
    #                                         height=(limits[3] - limits[2]).value,
    #                                         depth=(limits[5] - limits[4]).value)
    #     edges = p3.EdgesGeometry(box_geometry)
    #     return p3.LineSegments(geometry=edges,
    #                            material=p3.LineBasicMaterial(color='#000000'),
    #                            position=center.values.tolist())

    # def _get_limits(self):
    #     global_xmin = None
    #     global_xmax = None
    #     global_ymin = None
    #     global_ymax = None
    #     xscale = self._ax.get_xscale()
    #     yscale = self._ax.get_yscale()
    #     for child in self._children.values():
    #         xlims, ylims = child.get_limits(xscale=xscale, yscale=yscale)
    #         if isinstance(child, Line):
    #             if self._user_vmin is not None:
    #                 ylims[0] = self._user_vmin
    #             if self._user_vmax is not None:
    #                 ylims[1] = self._user_vmax
    #         if global_xmin is None or xlims[0].value < global_xmin:
    #             global_xmin = xlims[0].value
    #         if global_xmax is None or xlims[1].value > global_xmax:
    #             global_xmax = xlims[1].value
    #         if global_ymin is None or ylims[0].value < global_ymin:
    #             global_ymin = ylims[0].value
    #         if global_ymax is None or ylims[1].value > global_ymax:
    #             global_ymax = ylims[1].value

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
