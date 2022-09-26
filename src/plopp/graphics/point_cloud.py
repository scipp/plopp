# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from .color_mapper import ColorMapper
from .io import fig_to_bytes

import numpy as np
import scipp as sc
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase
import io
from PIL import Image


class PointCloud:

    def __init__(self,
                 data,
                 dim='position',
                 pixel_size=1,
                 cmap: str = None,
                 masks_cmap: str = "gray",
                 norm: str = "linear",
                 vmin=None,
                 vmax=None,
                 cbar=None):
        """
        Make a point cloud using pythreejs
        """
        import pythreejs as p3
        import ipywidgets as ipw
        self.color_mapper = ColorMapper(cmap=cmap,
                                        masks_cmap=masks_cmap,
                                        norm=norm,
                                        vmin=vmin,
                                        vmax=vmax)
        self._data = data
        self._dim = dim
        positions = self._data.meta[self._dim].values
        self.geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(array=positions.astype('float32')),
                'color':
                p3.BufferAttribute(
                    array=np.ones([positions.shape[0], 3], dtype='float32'))
            })

        pixel_ratio = 1.0  # config['plot']['pixel_ratio']
        # Note that an additional factor of 2.5 (obtained from trial and error) seems to
        # be required to get the sizes right in the scene.
        self.material = p3.PointsMaterial(vertexColors='VertexColors',
                                          size=2.5 * pixel_size * pixel_ratio,
                                          transparent=True)
        self.points = p3.Points(geometry=self.geometry, material=self.material)

        # self.scalar_map = cm.ScalarMappable(cmap='viridis')
        self._set_norm()

        self.colorbar = ipw.Image()

        self.update(new_values=data)

        # self.click_picker = p3.Picker(controlling=self.cbar, event='dblclick')

        # When the point selected by the picker changes, trigger our function:
        # self.click_picker.observe(self.toggle_norm, names=['point'])

        # Update figure:
        # renderer.controls = renderer.controls + [click_picker]
        # self.cbar = p3.LineSegments(geometry=p3.PlaneGeometry(width=0.1, height=0.4),
        #                             material=p3.MeshBasicMaterial(color='red')))

    def _set_points_colors(self):
        # colors = self.scalar_map.to_rgba(self._data.values)[..., :3]
        colors = self.color_mapper.rgba(self._data)[..., :3]
        # self._unit = array.unit

        # if 'mask' in new_values:
        #     # We change the colors of the points in-place where masks are True
        #     masks_inds = np.where(new_values['mask'].values)
        #     masks_colors = self.masks_scalar_map.to_rgba(
        #         array.values[masks_inds])[..., :3]
        #     colors[masks_inds] = masks_colors

        # colors = colors.astype('float32')
        self.geometry.attributes["color"].array = colors.astype('float32')
        # if "cut" in self.point_clouds:
        #     self.point_clouds["cut"].geometry.attributes["color"].array = colors[
        #         self.cut_surface_indices]

    def _update_colorbar(self):
        height_inches = 6
        cbar_fig = plt.figure(figsize=(height_inches * 0.2, height_inches), dpi=96)
        cbar_ax = cbar_fig.add_axes([0.05, 0.02, 0.25, 0.94])
        _ = ColorbarBase(cbar_ax,
                         cmap=self.color_mapper.cmap,
                         norm=self.color_mapper.norm_func)
        # if not isinstance(self.scalar_map.norm, LogNorm):
        #     _.formatter.set_useOffset(False)
        cbar_ax.set_ylabel(self._data.unit)
        # TODO If we set this position it is clipped somewhere. For now we
        # leave the default, which places unit to the right of the colorbar.
        # cbar_ax.yaxis.set_label_coords(-0.9, 0.5)
        # buf = io.BytesIO()
        # cbar_fig.savefig(buf, format='png')
        # plt.close(cbar_fig)
        # cbar_image = fig_to_pngbytes(cbar_fig)

        self.colorbar.value = fig_to_bytes(cbar_fig)
        plt.close(cbar_fig)
        # image = Image.open(buf)
        # image

        # self.cbar.material.map = p3.DataTexture(
        #     data=np.array(image, dtype='float32')[..., :3] / 255.0,
        #     format="RGBFormat",
        #     type="FloatType",
        # )
        # return np.flipud(np.array(image, dtype='float32')[..., :3] / 255.0)

    def update(self, new_values):
        self._data = new_values
        self.color_mapper.rescale(data=new_values.data)
        self._update_colorbar()
        self._set_points_colors()

    def _set_norm(self):
        self.color_mapper.set_norm(data=self._data.data)

    def toggle_norm(self, event):
        self.color_mapper.toggle_norm()
        self._set_norm()
        self._set_points_colors()
        self._update_colorbar()

    def get_limits(self):
        coord = self._data.meta[self._dim]
        xmin, xmax = fix_empty_range(find_limits(coord.fields.x))
        ymin, ymax = fix_empty_range(find_limits(coord.fields.y))
        zmin, zmax = fix_empty_range(find_limits(coord.fields.z))
        return (sc.concat([xmin, xmax], dim=f'{self._dim}.x'),
                sc.concat([ymin, ymax], dim=f'{self._dim}.y'),
                sc.concat([zmin, zmax], dim=f'{self._dim}.z'))
