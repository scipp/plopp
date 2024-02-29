# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from ..core import Node, View
from ..core.utils import make_compatible, name_with_unit


class GraphicalView(View):
    """ """

    def __init__(self, *nodes: Node):
        super().__init__(*nodes)
        self.colormapper = None

    def update(self, args=None, **kwargs):
        """ """

        new = kwargs
        if args is not None:
            new.update(args)

        for key, new_values in new.items():
            coords = {}
            for i, direction in enumerate(self._dims):
                if self._dims[direction] is None:
                    self._dims[direction] = new_values.dims[i]
                # elif self._dims[direction] != dim:
                #     raise ValueError(
                #         f"Dimension mismatch: {self._dims[direction]} != {dim}"
                #     )
                coords[direction] = new_values.coords[self._dims[direction]]

            if self.canvas.empty:
                axes_units = {k: coord.unit for k, coord in coords.items()}
                if 'y' not in self._dims:
                    axes_units['y'] = new_values.unit
                self.canvas.set_axes(dims=self._dims, units=axes_units)
                self.canvas.xlabel = name_with_unit(
                    var=coords['x'], name=self._dims['x']
                )
                if 'y' in self._dims:
                    self.canvas.ylabel = name_with_unit(
                        var=coords['y'], name=self._dims['y']
                    )
                    if self._dims['y'] in self._scale:
                        self.canvas.yscale = self._scale[self._dims['y']]
                else:
                    self.canvas.ylabel = name_with_unit(var=new_values.data, name="")
                if self.colormapper is not None:
                    self.colormapper.unit = new_values.unit
                if self._dims['x'] in self._scale:
                    self.canvas.xscale = self._scale[self._dims['x']]
            else:
                if self.colormapper is not None:
                    new_values.data = make_compatible(
                        new_values.data, unit=self.colormapper.unit
                    )
                for xy, dim in self._dims.items():
                    new_values.coords[dim] = make_compatible(
                        coords[xy], unit=self.canvas.units[xy]
                    )
                if 'y' not in self._dims:
                    new_values.data = make_compatible(
                        new_values.data, unit=self.canvas.units['y']
                    )

            if key not in self.artists:
                self.artists[key] = self.make_artist(new_values)
                if self.colormapper is not None:
                    self.colormapper[key] = self.artists[key]

            self.artists[key].update(new_values=new_values)

        if self.colormapper is not None:
            self.colormapper.update(args, **kwargs)
        self.canvas.autoscale()
