# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import name_with_unit
from .color_mapper import ColorMapper
from .io import fig_to_bytes
from ..widgets import ToggleTool

import numpy as np
import scipp as sc
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase


class PointCloud:

    def __init__(self,
                 *,
                 x,
                 y,
                 z,
                 data,
                 cbar,
                 figsize,
                 pixel_size=1,
                 cmap: str = None,
                 mask_cmap: str = "gray",
                 norm: str = "linear",
                 vmin=None,
                 vmax=None):
        """
        Make a point cloud using pythreejs
        """
        import pythreejs as p3
        import ipywidgets as ipw
        self.color_mapper = ColorMapper(cmap=cmap,
                                        mask_cmap=mask_cmap,
                                        norm=norm,
                                        vmin=vmin,
                                        vmax=vmax,
                                        nan_color="#f0f0f0")
        self._data = data
        self._x = x
        self._y = y
        self._z = z
        self._figsize = figsize

        self.geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(array=np.array([
                    self._data.meta[self._x].values.astype('float32'), self._data.meta[
                        self._y].values.astype('float32'), self._data.meta[
                            self._z].values.astype('float32')
                ]).T),
                'color':
                p3.BufferAttribute(array=np.ones([self._data.meta[self._x].shape[0], 3],
                                                 dtype='float32'))
            })

        pixel_ratio = 1.0  # config['plot']['pixel_ratio']
        # Note that an additional factor of 2.5 (obtained from trial and error) seems to
        # be required to get the sizes right in the scene.
        self.material = p3.PointsMaterial(vertexColors='VertexColors',
                                          size=2.5 * pixel_size * pixel_ratio,
                                          transparent=True)
        self.points = p3.Points(geometry=self.geometry, material=self.material)

        self._set_norm()
        self.colorbar = {
            'image':
            ipw.Image(),
            'button':
            ToggleTool(self.toggle_norm,
                       value=norm == 'log',
                       description='log',
                       tooltip='Toggle data norm').widget
        }
        self.update(new_values=data)
        self._update_colorbar()
        cbar.children = list(cbar.children) + list(self.colorbar.values())

    def _set_points_colors(self):
        colors = self.color_mapper.rgba(self._data)[..., :3]
        self.geometry.attributes["color"].array = colors.astype('float32')

    def _update_colorbar(self):
        dpi = 96
        height_inches = 0.89 * self._figsize[1] / dpi
        cbar_fig = plt.figure(figsize=(height_inches * 0.2, height_inches), dpi=dpi)
        cbar_ax = cbar_fig.add_axes([0.05, 0.02, 0.25, 1.0])
        _ = ColorbarBase(cbar_ax,
                         cmap=self.color_mapper.cmap,
                         norm=self.color_mapper.norm_func)
        cbar_ax.set_ylabel(name_with_unit(self._data.data, name=self._data.name))
        self.colorbar['image'].value = fig_to_bytes(cbar_fig)
        plt.close(cbar_fig)

    def update(self, new_values):
        self._data = new_values
        old_bounds = [self.color_mapper.vmin, self.color_mapper.vmax]
        self.color_mapper.rescale(data=new_values.data)
        if old_bounds != [self.color_mapper.vmin, self.color_mapper.vmax]:
            self._update_colorbar()
        self._set_points_colors()

    def _set_norm(self):
        self.color_mapper.set_norm(data=self._data.data)

    def toggle_norm(self):
        self.color_mapper.toggle_norm()
        self._set_norm()
        self._set_points_colors()
        self._update_colorbar()

    def get_limits(self):
        xmin, xmax = fix_empty_range(find_limits(self._data.meta[self._x]))
        ymin, ymax = fix_empty_range(find_limits(self._data.meta[self._y]))
        zmin, zmax = fix_empty_range(find_limits(self._data.meta[self._z]))
        return (sc.concat([xmin, xmax],
                          dim=self._x), sc.concat([ymin, ymax], dim=self._y),
                sc.concat([zmin, zmax], dim=self._z))
