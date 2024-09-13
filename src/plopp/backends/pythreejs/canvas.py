# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from __future__ import annotations

from copy import copy
from typing import Any

import ipywidgets as ipw
import numpy as np
import scipp as sc

from ...graphics import Camera
from ...graphics.bbox import BoundingBox


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
        The title to be placed above the figure. It is possible to use HTML formatting
        to customize the title appearance.
    camera:
        Initial camera configuration (position, target).
    """

    def __init__(
        self,
        figsize: tuple[int, int] | None = None,
        title: str | None = None,
        camera: Camera | None = None,
        **ignored,
    ):
        import pythreejs as p3

        self.dims = {}
        self.units = {}
        self.xscale = 'linear'
        self.yscale = 'linear'
        self.zscale = 'linear'
        self.outline = None
        self.axticks = None
        self.figsize = np.asarray(figsize if figsize is not None else (600, 400))
        self._title_text = title
        self._title = self._make_title()
        width, height = self.figsize
        self._user_camera = Camera() if camera is None else camera
        self.camera = p3.PerspectiveCamera(aspect=width / height)
        self.camera_backup = {}
        self.axes_3d = p3.AxesHelper()
        self.bbox = BoundingBox()
        self._cached_limits = None
        self.scene = p3.Scene(
            children=[self.camera, self.axes_3d], background="#f0f0f0"
        )
        self.controls = p3.OrbitControls(controlling=self.camera)
        self.renderer = p3.Renderer(
            camera=self.camera,
            scene=self.scene,
            controls=[self.controls],
            width=width,
            height=height,
        )

    def to_widget(self):
        # The max_width is set to prevent overflow, see
        # https://github.com/scipp/plopp/issues/169.
        # See also https://github.com/scipp/plopp/pull/367.
        self.renderer.layout = ipw.Layout(max_width='100%', overflow='auto')
        return self.renderer

    def set_axes(self, dims, units, dtypes):
        """
        Set the axes dimensions and units.

        Parameters
        ----------
        dims:
            The dimensions of the data.
        units:
            The units of the data.
        dtypes:
            The data types of the data.
        """
        self.units = units
        self.dims = dims
        self.dtypes = dtypes

    def draw(self):
        """
        Create an outline box with ticklabels, given a range in the XYZ directions.
        """
        from .outline import Outline

        # If `None` is found in the limits, it means we are waiting first for a call
        # to autoscale on the parent view.
        if self.empty or (None in self.bbox.asdict().values()):
            return

        limits = (
            sc.array(dims=[self.dims['x']], values=self.xrange, unit=self.units['x']),
            sc.array(dims=[self.dims['y']], values=self.yrange, unit=self.units['y']),
            sc.array(dims=[self.dims['z']], values=self.zrange, unit=self.units['z']),
        )

        if self._cached_limits is not None:
            if all(
                sc.allclose(lim, cached_lim)
                for lim, cached_lim in zip(limits, self._cached_limits, strict=True)
            ):
                return

        self._cached_limits = limits

        if self.outline is not None:
            self.remove(self.outline)
        self.outline = Outline(limits=limits)
        self.add(self.outline)
        # Update the camera position when a new object is added to the canvas.
        # The camera will look at the mean position of all the objects, and its position
        # will be far enough from the center to see all the objects.
        # This 'Home' position will be backed up so it can be used when resetting the
        # camera via the ``home`` function.
        if not self._user_camera.has_units():
            self._user_camera.set_units(
                self.units.get('x'), self.units.get('y'), self.units.get('z')
            )

        center = [var.mean().value for var in limits]
        distance_fudge_factor = 1.2
        box_size = np.array([(limits[i][1] - limits[i][0]).value for i in range(3)])
        self.camera.position = self._user_camera.get(
            'position', list(np.array(center) + distance_fudge_factor * box_size)
        )
        camera_dist = np.linalg.norm(np.array(self.camera.position) - np.array(center))
        box_mean_size = np.linalg.norm(box_size)
        self.camera.near = self._user_camera.get('near', 0.01 * box_mean_size)
        camera_to_origin = np.linalg.norm(
            np.array(self.camera.position) - np.array([0, 0, 0])
        )
        center_to_origin = np.linalg.norm(np.array(center) - np.array([0, 0, 0]))
        self.camera.far = self._user_camera.get(
            'far',
            5 * max(box_mean_size, camera_dist, camera_to_origin, center_to_origin),
        )
        camera_lookat = tuple(self._user_camera.get('look_at', center))
        self.controls.target = camera_lookat
        self.camera.lookAt(camera_lookat)

        # Save camera settings
        self.camera_backup["reset"] = copy(self.camera.position)
        self.camera_backup["look_at"] = copy(camera_lookat)
        self.camera_backup["center"] = tuple(copy(center))
        self.camera_backup["x_normal"] = [
            center[0] - distance_fudge_factor * box_mean_size,
            center[1],
            center[2],
        ]
        self.camera_backup["y_normal"] = [
            center[0],
            center[1] - distance_fudge_factor * box_mean_size,
            center[2],
        ]
        self.camera_backup["z_normal"] = [
            center[0],
            center[1],
            center[2] - distance_fudge_factor * box_mean_size,
        ]
        self.axes_3d.scale = [self.camera.far] * 3

    @property
    def empty(self) -> bool:
        """
        Check if the canvas is empty.
        """
        return not self.dims

    def home(self):
        """
        Reset the camera position.
        """
        self.move_camera(
            position=self.camera_backup["reset"], look_at=self.camera_backup["look_at"]
        )

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

    def _camera_normal(self, position: tuple[float, float, float], ind: int):
        """
        Move camera to requested normal, and flip if current position is equal
        to the requested position.
        """
        if np.allclose(self.camera.position, position):
            position[ind] = 2.0 * self.camera_backup["center"][ind] - position[ind]
        self.move_camera(position=position)

    def move_camera(
        self,
        position: tuple[float, float, float],
        look_at: tuple[float, float, float] | None = None,
    ):
        """
        Move the camera to the supplied position.

        Parameters
        ----------
        position:
            The new camera position.
        """
        self.camera.position = position
        if look_at is None:
            look_at = self.camera_backup["center"]
        self.controls.target = look_at
        self.camera.lookAt(look_at)

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

    def _make_title(self):
        if self._title_text:
            html = (
                f'<div style="text-align: center; width: {self.figsize[0]}px">'
                f'{self._title_text}</div>'
            )
        else:
            html = None
        return ipw.HTML(html)

    @property
    def title(self) -> str:
        """
        Get or set the title of the plot.
        """
        return self._title_text

    @title.setter
    def title(self, text: str):
        self._title_text = text
        self._title = self._make_title()

    def bigger(self):
        self.figsize = (self.figsize * 1.2).astype(int)
        self._update_size()

    def smaller(self):
        self.figsize = (self.figsize / 1.2).astype(int)
        self._update_size()

    def _update_size(self):
        self.renderer.width = self.figsize[0]
        self.renderer.height = self.figsize[1]
        self.camera.aspect = self.figsize[0] / self.figsize[1]

    @property
    def xmin(self) -> float:
        """
        Get or set the minimum x-axis value.
        """
        return self.bbox.xmin

    @xmin.setter
    def xmin(self, value: float):
        self.bbox.xmin = value

    @property
    def xmax(self) -> float:
        """
        Get or set the maximum x-axis value.
        """
        return self.bbox.xmax

    @xmax.setter
    def xmax(self, value: float):
        self.bbox.xmax = value

    @property
    def xrange(self) -> tuple[float, float]:
        """
        Get or set the range/limits of the x-axis.
        """
        return (self.xmin, self.xmax)

    @xrange.setter
    def xrange(self, value: tuple[float, float]):
        self.xmin, self.xmax = value

    @property
    def ymin(self) -> float:
        """
        Get or set the minimum y-axis value.
        """
        return self.bbox.ymin

    @ymin.setter
    def ymin(self, value: float):
        self.bbox.ymin = value

    @property
    def ymax(self) -> float:
        """
        Get or set the maximum y-axis value.
        """
        return self.bbox.ymax

    @ymax.setter
    def ymax(self, value: float):
        self.bbox.ymax = value

    @property
    def yrange(self) -> tuple[float, float]:
        """
        Get or set the range/limits of the y-axis.
        """
        return (self.ymin, self.ymax)

    @yrange.setter
    def yrange(self, value: tuple[float, float]):
        self.ymin, self.ymax = value

    @property
    def zmin(self) -> float:
        """
        Get or set the minimum z-axis value.
        """
        return self.bbox.zmin

    @zmin.setter
    def zmin(self, value: float):
        self.bbox.zmin = value

    @property
    def zmax(self) -> float:
        """
        Get or set the maximum z-axis value.
        """
        return self.bbox.zmax

    @zmax.setter
    def zmax(self, value: float):
        self.bbox.zmax = value

    @property
    def zrange(self) -> tuple[float, float]:
        """
        Get or set the range/limits of the z-axis.
        """
        return (self.zmin, self.zmax)

    @zrange.setter
    def zrange(self, value: tuple[float, float]):
        self.zmin, self.zmax = value

    def update_legend(self):
        pass
