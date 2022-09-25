# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range

import pythreejs as p3
import numpy as np
from matplotlib import cm


def _make_axis_tick(self, string, position, color="black", size=1.0):
    """
    Make a text-based sprite for axis tick
    """
    sm = p3.SpriteMaterial(map=p3.TextTexture(string=string,
                                              color=color,
                                              size=300,
                                              squareTexture=True),
                           transparent=True)
    return p3.Sprite(material=sm, position=position, scale=[size, size, size])


class Outline:

    def __init__(self, limits):
        """
        Make a point cloud using pythreejs
        """
        center = sc.concat(limits, dim='x').fold('x', sizes={'x': 3, 'y': 2}).mean('y')

        self._geometry = p3.BoxBufferGeometry(width=(limits[1] - limits[0]).value,
                                              height=(limits[3] - limits[2]).value,
                                              depth=(limits[5] - limits[4]).value)
        self._edges = p3.EdgesGeometry(self._geometry)
        self.line = p3.LineSegments(geometry=self._edges,
                                    material=p3.LineBasicMaterial(color='#000000'),
                                    position=center.values.tolist())
        self.ticks = self._generate_axis_ticks_and_labels(limits)

    def _generate_axis_ticks_and_labels(self, *, limits, box_size, components):
        """
        Create ticklabels on outline edges
        """
        # if self.tick_size is None:
        tick_size = 0.05 * np.mean(box_size)
        ticks_and_labels = p3.Group()
        iden = np.identity(3, dtype=np.float32)
        ticker_ = ticker.MaxNLocator(5)
        lims = {x: limits[x] for x in "xyz"}

        def get_offsets(dim, ind):
            if dim == 'x':
                return np.array([0, limits['y'][ind], limits['z'][ind]])
            if dim == 'y':
                return np.array([limits['x'][ind], 0, limits['z'][ind]])
            if dim == 'z':
                return np.array([limits['x'][ind], limits['y'][ind], 0])

        for axis, (x, dim) in enumerate(zip('xyz', components)):
            ticks = ticker_.tick_values(lims[x][0], lims[x][1])
            for tick in ticks:
                if lims[x][0] <= tick <= lims[x][1]:
                    tick_pos = iden[axis] * tick + get_offsets(x, 0)
                    ticks_and_labels.add(
                        self._make_axis_tick(string=value_to_string(tick, precision=1),
                                             position=tick_pos.tolist(),
                                             size=self.tick_size))
            coord = components[dim]
            axis_label = f'{dim} [{coord.unit}]' if self.axlabels[
                x] is None else self.axlabels[x]
            # Offset labels 5% beyond axis ticks to reduce overlap
            delta = 0.05
            ticks_and_labels.add(
                self._make_axis_tick(string=axis_label,
                                     position=(iden[axis] * 0.5 * np.sum(limits[x]) +
                                               (1.0 + delta) * get_offsets(x, 0) -
                                               delta * get_offsets(x, 1)).tolist(),
                                     size=self.tick_size * 0.3 * len(axis_label)))

        return ticks_and_labels

    def _update_colors(self):
        colors = self.scalar_map.to_rgba(self._data.values)[..., :3]
        # self._unit = array.unit

        # if 'mask' in new_values:
        #     # We change the colors of the points in-place where masks are True
        #     masks_inds = np.where(new_values['mask'].values)
        #     masks_colors = self.masks_scalar_map.to_rgba(
        #         array.values[masks_inds])[..., :3]
        #     colors[masks_inds] = masks_colors

        colors = colors.astype('float32')
        self.geometry.attributes["color"].array = colors
        # if "cut" in self.point_clouds:
        #     self.point_clouds["cut"].geometry.attributes["color"].array = colors[
        #         self.cut_surface_indices]

    def update(self, new_values):
        self._data = new_values
        self._update_colors()

    def get_limits(self):
        coord = self._data.meta[self._dim]
        xmin, xmax = fix_empty_range(find_limits(coord.fields.x))
        ymin, ymax = fix_empty_range(find_limits(coord.fields.y))
        zmin, zmax = fix_empty_range(find_limits(coord.fields.z))
        return xmin, xmax, ymin, ymax, zmin, zmax
