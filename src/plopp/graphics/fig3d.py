# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

# from .fig3d import Fig3d

import scipp as sc
from .basefig import BaseFig
from .colormapper import ColorMapper

# class ScatterFig(View, VBox):

#     should contain a Canvas3d, a toolbar,


class Figure3d(BaseFig):

    def __init__(self,
                 *nodes,
                 x,
                 y,
                 z,
                 figsize=None,
                 title=None,
                 cmap: str = 'viridis',
                 mask_cmap: str = 'gray',
                 norm=None,
                 vmin=None,
                 vmax=None,
                 **kwargs):

        super().__init__(*nodes)

        self._x = x
        self._y = y
        self._z = z
        self._kwargs = kwargs

        from .canvas3d import Canvas3d
        self.canvas = Canvas3d(figsize=figsize)
        self.colormapper = ColorMapper(cmap=cmap,
                                       mask_cmap=mask_cmap,
                                       norm=norm,
                                       vmin=vmin,
                                       vmax=vmax,
                                       nan_color="#f0f0f0",
                                       figheight=self.canvas.figsize[1])

        # self.right_bar.add(self.colormapper.to_widget)
        # self.colormapper.colorbar['button'].on_click()

        self._original_children = [n.id for n in nodes]
        self.render()

        # self._original_children = list(self._children.keys())

    def update(self, new_values: sc.DataArray, key: str, draw=True):
        """
        Update image array with new values.
        """

        self.colormapper.update(data=new_values)

        # from .outline import Outline

        # if key in self._original_children:
        #     self.colormapper.autoscale(new_values)

        if key not in self._children:
            # if colormapper is not None:
            #     colormapper = self._children[colormapper].color_mapper
            from .point_cloud import PointCloud
            pts = PointCloud(
                data=new_values,
                x=self._x,
                y=self._y,
                z=self._z,
                # colormapper=self.colormapper,
                # figheight=self._figheight,
                **self._kwargs)
            self._children[key] = pts
            self.colormapper[key] = pts
            self.canvas.add(pts.points)
            print(key, self._original_children)
            if key in self._original_children:
                print('making outline')
                self.canvas.make_outline(limits=self.get_limits())
                # if self.outline is not None:
                #     self.scene.remove(self.outline)
                # self.outline = Outline(limits=limits)
                # self.scene.add(self.outline)
                # self._update_camera(limits=limits)
                # self.axes_3d.scale = [self.camera.far] * 3

        self._children[key].update(new_values=new_values)
        self._children[key].set_colors(self.colormapper.rgba(self._children[key].data))

    def get_limits(self):
        """
        Get global limits for all the point clouds in the scene.
        """
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        zmin = None
        zmax = None
        for child in self._children.values():
            xlims, ylims, zlims = child.get_limits()
            if xmin is None or xlims[0] < xmin:
                xmin = xlims[0]
            if xmax is None or xlims[1] > xmax:
                xmax = xlims[1]
            if ymin is None or ylims[0] < ymin:
                ymin = ylims[0]
            if ymax is None or ylims[1] > ymax:
                ymax = ylims[1]
            if zmin is None or zlims[0] < zmin:
                zmin = zlims[0]
            if zmax is None or zlims[1] > zmax:
                zmax = zlims[1]
        return (sc.concat([xmin, xmax],
                          dim=self._x), sc.concat([ymin, ymax], dim=self._y),
                sc.concat([zmin, zmax], dim=self._z))

    def set_opacity(self, alpha):
        """
        Update the opacity of the original children (not the cuts).
        """
        for name in self._original_children:
            self._children[name].opacity = alpha

    def remove(self, key):
        """
        Remove an object from the scene.
        """
        self.canvas.remove(self._children[key].points)
        del self._children[key]
