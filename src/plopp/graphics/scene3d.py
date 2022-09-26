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

        # Add red/green/blue axes helper
        self.axes_3d = p3.AxesHelper()

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

        self.toolbar = Toolbar(tools={'home': self.home})

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
            pts = PointCloud(data=new_values, **self._kwargs)
            self._children[key] = pts
            limits = self._children[key].get_limits()
            # center = sc.concat(limits, dim='x').fold('x', sizes={
            #     'x': 3,
            #     'y': 2
            # }).mean('y')
            self.outline = Outline(limits=limits)
            self.scene.add(pts.points)
            self.scene.add(self.outline.all)
            self.right_bar.children = list(self.right_bar.children) + [pts.colorbar]

            # self.camera.add(self._children[key].cbar)
            # self.camera.near = 0.01
            # self._children[key].cbar.position = [0.6, 0, -1]
            # self.renderer.controls = self.renderer.controls + [
            #     self._children[key].click_picker
            # ]
        else:
            self._children[key].update(new_values=new_values)

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
    def home(self):
        return

    def render(self):
        for node in self.graph_nodes.values():
            new_values = node.request_data()
            self.update(new_values=new_values, key=node.id)
