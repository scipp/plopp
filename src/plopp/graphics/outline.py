# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from ..core.limits import find_limits, fix_empty_range
from ..core.utils import value_to_string

import pythreejs as p3
import numpy as np
from matplotlib import ticker


def _make_sprite(string, position, color="black", size=1.0):
    """
    Make a text-based sprite for axis tick
    """
    sm = p3.SpriteMaterial(map=p3.TextTexture(string=string,
                                              color=color,
                                              size=300,
                                              squareTexture=True),
                           transparent=True)
    return p3.Sprite(material=sm, position=position, scale=[size, size, size])


def _get_delta(x, axis):
    return (x[axis][1] - x[axis][0]).value


def _get_offsets(limits, axis, ind):
    offsets = np.array([limits[i][ind].value for i in range(3)])
    offsets[axis] = 0
    return offsets


class Outline:

    def __init__(self, limits, tick_size=None):
        """
        Make a point cloud using pythreejs
        """
        # center = sc.concat(limits, dim='x').fold('x', sizes={'x': 3, 'y': 2}).mean('y')
        if tick_size is None:
            tick_size = 0.05 * np.mean([_get_delta(limits, axis=i) for i in range(3)])

        center = [var.mean().value for var in limits]

        self._geometry = p3.BoxBufferGeometry(width=_get_delta(limits, axis=0),
                                              height=_get_delta(limits, axis=1),
                                              depth=_get_delta(limits, axis=2))
        self._edges = p3.EdgesGeometry(self._geometry)
        self.box = p3.LineSegments(geometry=self._edges,
                                   material=p3.LineBasicMaterial(color='#000000'),
                                   position=center)
        self.ticks = self._make_ticks(limits=limits, center=center, tick_size=tick_size)
        self.labels = self._make_labels(limits=limits,
                                        center=center,
                                        tick_size=tick_size)
        self.all = p3.Group()
        for obj in (self.box, self.ticks, self.labels):
            self.all.add(obj)

    def _make_ticks(self, limits, center, tick_size):
        """
        Create ticklabels on outline edges
        """
        ticks_group = p3.Group()
        iden = np.identity(3, dtype=np.float32)
        ticker_ = ticker.MaxNLocator(5)
        for axis in range(3):
            ticks = ticker_.tick_values(limits[axis][0].value, limits[axis][1].value)
            for tick in ticks:
                if limits[axis][0].value <= tick <= limits[axis][1].value:
                    tick_pos = iden[axis] * tick + _get_offsets(limits, axis, 0)
                    ticks_group.add(
                        _make_sprite(string=value_to_string(tick, precision=1),
                                     position=tick_pos.tolist(),
                                     size=tick_size))
        return ticks_group

    def _make_labels(self, limits, center, tick_size):
        """
        Create ticklabels on outline edges
        """
        labels_group = p3.Group()
        # iden = np.identity(3, dtype=np.float32)
        for axis in range(3):
            axis_label = f'{limits[axis].dim} [{limits[axis].unit}]'
            # Offset labels 5% beyond axis ticks to reduce overlap
            delta = 0.05
            labels_group.add(
                _make_sprite(string=axis_label,
                             position=(np.roll([1, 0, 0], axis) * center[axis] +
                                       (1.0 + delta) * _get_offsets(limits, axis, 0) -
                                       delta * _get_offsets(limits, axis, 1)).tolist(),
                             size=tick_size * 0.3 * len(axis_label)))

        return labels_group

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
