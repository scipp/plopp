# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

from ..core import Node, View
from ..core.utils import make_compatible, name_with_unit


class GraphicalView(View):
    """
    Base class for graphical 1d and 2d views.
    It is used to represent line plots, scatter plots, and image plots (heatmaps).
    In addition to ``View``, it updates the canvas axes and labels when new data is
    supplied.
    It also verifies that the new data supplied is compatible with the existing axes
    dimensions and units.
    """

    def __init__(self, *nodes: Node):
        super().__init__(*nodes)
        self.colormapper = None

    def update(self, *args, **kwargs):
        """
        Update the view with new data by either supplying a dictionary of
        new data or by keyword arguments.
        """

        new = dict(*args, **kwargs)
        for key, new_values in new.items():
            if new_values.ndim != self._ndim:
                raise ValueError(
                    f"Expected {self._ndim} dimension(s), but got {new_values.ndim}."
                )

            coords = {}
            for i, direction in enumerate(self._dims):
                if self._dims[direction] is None:
                    self._dims[direction] = new_values.dims[i]
                coords[direction] = new_values.coords[self._dims[direction]]

            if self.canvas.empty:
                axes_units = {k: coord.unit for k, coord in coords.items()}
                axes_dtypes = {k: coord.dtype for k, coord in coords.items()}
                if 'y' in self._dims:
                    self.canvas.ylabel = name_with_unit(
                        var=coords['y'], name=self._dims['y']
                    )
                    if self._dims['y'] in self._scale:
                        self.canvas.yscale = self._scale[self._dims['y']]
                else:
                    self.canvas.ylabel = name_with_unit(var=new_values.data, name="")
                    axes_units['y'] = new_values.unit
                    axes_dtypes['y'] = new_values.dtype

                self.canvas.set_axes(
                    dims=self._dims, units=axes_units, dtypes=axes_dtypes
                )
                self.canvas.xlabel = name_with_unit(
                    var=coords['x'], name=self._dims['x']
                )
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
            self.colormapper.update(**new)
        self.canvas.autoscale()
