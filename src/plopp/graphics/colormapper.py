# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from copy import copy
from functools import reduce
from typing import Any, Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipp as sc
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Colormap, LinearSegmentedColormap, LogNorm, Normalize

from ..backends.matplotlib.utils import fig_to_bytes
from ..core.limits import find_limits, fix_empty_range
from ..core.utils import maybe_variable_to_number, merge_masks
from ..utils import parse_vmin_vmax_norm


def _shift_color(color: float, delta: float) -> float:
    """
    Shift a color (number from 0 to 1) by delta. If the result is out of bounds,
    the color is shifted in the opposite direction.
    """
    shifted = color + delta
    if shifted > 1.0 or shifted < 0.0:
        return color - delta
    return shifted


def _get_cmap(colormap: str | Colormap, nan_color: str | None = None) -> Colormap:
    """
    Get a colormap object from a colormap name.
    We also set the 'over', 'under' and 'bad' colors. The 'bad' color is set to
    ``nan_color`` if it is not None. The 'over' and 'under' colors are set to be
    slightly lighter or darker than the first and last colors in the colormap.

    Parameters
    ----------
    colormap:
        Name of the colormap. If the name is just a single html color, this will
        create a colormap with that single color. If ``cmap`` is already a Colormap,
        it will be used as is.
    nan_color:
        The color to use for NAN values.
    """

    if isinstance(colormap, Colormap):
        return colormap

    try:
        if hasattr(mpl, 'colormaps'):
            cmap = copy(mpl.colormaps[colormap])
        else:
            cmap = mpl.cm.get_cmap(colormap)
    except (KeyError, ValueError):
        cmap = LinearSegmentedColormap.from_list('tmp', [colormap, colormap])

    # Add under and over values to the cmap
    delta = 0.15
    cmap = cmap.copy()
    over = cmap.get_over()
    under = cmap.get_under()
    # Note that we only shift the first 3 RGB values, leaving alpha unchanged.
    cmap.set_over(
        [_shift_color(c, delta * (-1 + 2 * (np.mean(over) > 0.5))) for c in over[:3]]
    )
    cmap.set_under(
        [_shift_color(c, delta * (-1 + 2 * (np.mean(under) > 0.5))) for c in under[:3]]
    )

    if nan_color is not None:
        cmap.set_bad(color=nan_color)
    return cmap


def _get_normalizer(norm: str) -> Normalize:
    """
    Get an appropriate normalizer depending on the scaling.
    """
    return Normalize(vmin=0, vmax=1) if norm == 'linear' else LogNorm(vmin=1, vmax=2)


class ColorMapper:
    """
    A class that handles conversion between data values and RGBA colors.
    It controls the normalization (linear or log), as well as the min and max limits
    for the color range.

    Parameters
    ----------
    cax:
        The axes to use for the colorbar. If none are supplied, the ColorMapper will
        create its own axes.
    cbar:
        Create a colorbar if ``True``. If ``False``, no colorbar is made even if ``cax``
        is defined.
    cmap:
        The name of the colormap for the data
        (see https://matplotlib.org/stable/tutorials/colors/colormaps.html).
        In addition to the Matplotlib docs, if the name is just a single html color,
        a colormap with that single color will be used.
    mask_cmap:
        The name of the colormap for masked data.
    cmin:
        The minimum value for the colorscale range. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the data unit.
    cmax:
        The maximum value for the colorscale range. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the data unit.
    logc:
        If ``True``, use a logarithmic colorscale.
    nan_color:
        The color used for representing NAN values.
    figsize:
        The size of the figure next to which the colorbar will be displayed.
    norm:
        The colorscale normalization. This is an old parameter name.
        Prefer using ``logc`` instead.
    vmin:
        The minimum value for the colorscale range. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the data unit.
        This is an old parameter name. Prefer using ``cmin`` instead.
    vmax:
        The maximum value for the colorscale range. If a number (without a unit) is
        supplied, it is assumed that the unit is the same as the data unit.
        This is an old parameter name. Prefer using ``cmax`` instead.
    """

    def __init__(
        self,
        canvas: Any | None = None,
        cbar: bool = True,
        cmap: str | Colormap = 'viridis',
        mask_cmap: str | Colormap = 'gray',
        cmin: sc.Variable | float | None = None,
        cmax: sc.Variable | float | None = None,
        logc: bool = False,
        clabel: str | None = None,
        nan_color: str | None = None,
        figsize: tuple[float, float] | None = None,
        norm: Literal['linear', 'log', None] = None,
        vmin: sc.Variable | float | None = None,
        vmax: sc.Variable | float | None = None,
    ):
        cmin, cmax, logc = parse_vmin_vmax_norm(
            vmin=vmin,
            vmax=vmax,
            norm=norm,
            ymin=cmin,
            ymax=cmax,
            log=logc,
            y_or_c='c',
        )

        self._canvas = canvas
        self.cax = self._canvas.cax if hasattr(self._canvas, 'cax') else None
        self.cmap = _get_cmap(cmap, nan_color=nan_color)
        self.mask_cmap = _get_cmap(mask_cmap, nan_color=nan_color)
        self.user_cmin = cmin
        self.user_cmax = cmax
        self._cmin = np.inf
        self._cmax = -np.inf
        self._clabel = clabel
        self._logc = logc
        self.set_colors_on_update = True

        # Note that we need to set cmin/cmax for the LogNorm, if not an error is
        # raised when making the colorbar before any call to update is made.
        self.normalizer = _get_normalizer('log' if self._logc else 'linear')
        self.colorbar = None
        self._unit = None
        self.empty = True
        self.changed = False
        self.artists = {}
        self.widget = None

        if cbar:
            if self.cax is None:
                dpi = 100
                height_inches = (figsize[1] / dpi) if figsize is not None else 6
                fig = plt.Figure(figsize=(height_inches * 0.2, height_inches))
                self.cax = fig.add_axes([0.05, 0.02, 0.2, 0.98])
            self.colorbar = ColorbarBase(self.cax, cmap=self.cmap, norm=self.normalizer)
            self.cax.yaxis.set_label_coords(-0.9, 0.5)
            if clabel is not None:
                self.cax.set_ylabel(clabel)

    def add_artist(self, key: str, artist: Any):
        self.artists[key] = artist

    def remove_artist(self, key: str):
        del self.artists[key]

    def to_widget(self):
        """
        Convert the colorbar into a widget for use with other ``ipywidgets``.
        """
        import ipywidgets as ipw

        self.widget = ipw.HTML()
        self._update_colorbar_widget()
        return self.widget

    def _update_colorbar_widget(self):
        """
        Upon an updated colorscale range, we need to update the image inside the widget.
        """
        if self.widget is not None:
            self.widget.value = fig_to_bytes(self.cax.get_figure(), form='svg').decode()

    def rgba(self, data: sc.DataArray) -> np.ndarray:
        """
        Return rgba values given a data array.

        Parameters
        ----------
        data:
            The data array to be converted to rgba colors, taking masks into account.
        """
        colors = self.cmap(self.normalizer(data.values))
        if data.masks:
            one_mask = sc.broadcast(merge_masks(data.masks), sizes=data.sizes).values
            colors[one_mask] = self.mask_cmap(self.normalizer(data.values[one_mask]))
        return colors

    def autoscale(self):
        """
        Re-compute the global min and max range of values by iterating over all the
        artists and adjust the limits.
        """
        limits = [
            fix_empty_range(
                find_limits(artist._data, scale='log' if self._logc else 'linear')
            )
            for artist in self.artists.values()
        ]
        cmin = reduce(min, [v[0] for v in limits])
        cmax = reduce(max, [v[1] for v in limits])
        if self.user_cmin is not None:
            self._cmin = self.user_cmin
        else:
            self._cmin = cmin.value
        if self.user_cmax is not None:
            self._cmax = self.user_cmax
        else:
            self._cmax = cmax.value

        if self._cmin >= self._cmax:
            if self.user_cmax is not None:
                self._cmax = self.user_cmax
                self._cmin = self.user_cmax - abs(self.user_cmax) * 0.1
            else:
                self._cmin = self.user_cmin
                self._cmax = self.user_cmin + abs(self.user_cmin) * 0.1

        self.apply_limits()

    def apply_limits(self):
        # Synchronize the underlying normalizer limits to the current state.
        # Note that the order matters here, as for a normalizer cmin cannot be set above
        # the current cmax.
        if self._cmin >= self.normalizer.vmax:
            self.normalizer.vmax = self._cmax
            self.normalizer.vmin = self._cmin
        else:
            self.normalizer.vmin = self._cmin
            self.normalizer.vmax = self._cmax

        if self.colorbar is not None:
            self._update_colorbar_widget()
        self.notify_artists()

    def notify_artists(self):
        """
        Notify the artists that the state of the colormapper has changed.
        """
        for artist in self.artists.values():
            artist.notify_artist('colormap changed')

    @property
    def vmin(self) -> float:
        """
        Get or set the minimum value of the colorbar.
        This is an old property name. Prefer using ``cmin`` instead.
        """
        return self.cmin

    @vmin.setter
    def vmin(self, vmin: sc.Variable | float):
        self.cmin = vmin

    @property
    def vmax(self) -> float:
        """
        Get or set the maximum value of the colorbar.
        This is an old property name. Prefer using ``cmax`` instead.
        """
        return self.cmax

    @vmax.setter
    def vmax(self, vmax: sc.Variable | float):
        self.cmax = vmax

    @property
    def cmin(self) -> float:
        """
        Get or set the minimum value of the colorbar.
        """
        return self._cmin

    @cmin.setter
    def cmin(self, cmin: sc.Variable | float):
        self._cmin = maybe_variable_to_number(cmin, unit=self._unit)
        self.apply_limits()

    @property
    def cmax(self) -> float:
        """
        Get or set the maximum value of the colorbar.
        """
        return self._cmax

    @cmax.setter
    def cmax(self, cmax: sc.Variable | float):
        self._cmax = maybe_variable_to_number(cmax, unit=self._unit)
        self.apply_limits()

    @property
    def unit(self) -> str | None:
        """
        Get or set the unit of the colorbar.
        """
        return self._unit

    @unit.setter
    def unit(self, unit: str | None):
        self._unit = unit
        if self.user_cmin is not None:
            self.user_cmin = maybe_variable_to_number(self.user_cmin, unit=self._unit)
        if self.user_cmax is not None:
            self.user_cmax = maybe_variable_to_number(self.user_cmax, unit=self._unit)

    @property
    def clabel(self) -> str | None:
        """
        Get or set the label of the colorbar axis.
        """
        if self.cax is not None:
            return self.cax.get_ylabel()

    @clabel.setter
    def clabel(self, lab: str):
        if self.cax is not None:
            self.cax.set_ylabel(lab)

    @property
    def ylabel(self) -> str | None:
        """
        Get or set the label of the colorbar axis.
        This is an old property name. Prefer using ``clabel`` instead.
        """
        return self.clabel

    @ylabel.setter
    def ylabel(self, lab: str):
        self.clabel = lab

    def toggle_norm(self):
        """
        Toggle the norm flag, between `linear` and `log`.
        """
        # self.norm = "log" if self.norm == 'linear' else 'linear'
        self._logc = not self._logc
        self.normalizer = _get_normalizer('log' if self._logc else 'linear')
        self._cmin = np.inf
        self._cmax = -np.inf
        if self.colorbar is not None:
            self.colorbar.mappable.norm = self.normalizer
        self.autoscale()
        if self._canvas is not None:
            self._canvas.draw()

    @property
    def norm(self) -> Literal['linear', 'log']:
        """
        Get or set the colorscale normalization.
        """
        return 'log' if self._logc else 'linear'

    @norm.setter
    def norm(self, norm: Literal['linear', 'log']):
        if norm not in ['linear', 'log']:
            raise ValueError('norm must be either "linear" or "log".')
        if norm != self.norm:
            self.toggle_norm()
