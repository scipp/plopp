# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import inspect
from collections.abc import Callable, Sequence
from typing import Literal

import scipp as sc


def _add_signature_params(
    func, extra_params: Sequence[inspect.Parameter], *, before_var_kw=True
) -> Callable:
    """
    Return `func` with extra parameters injected into its __signature__.

    Parameters
    ----------
    func : callable
        The function whose signature to extend.
    extra_params : list of inspect.Parameter
        Parameters to add.
    before_var_kw : bool, default True
        If True, insert new parameters before any **kwargs.
        If False, append them at the end.
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    existing_names = {p.name for p in params}

    # Keep only those not already present
    filtered_extra = [p for p in extra_params if p.name not in existing_names]

    if not filtered_extra:  # nothing to add
        return func

    if before_var_kw:
        try:
            idx = next(
                i
                for i, p in enumerate(params)
                if p.kind == inspect.Parameter.VAR_KEYWORD
            )
        except StopIteration:
            idx = len(params)
        new_params = params[:idx] + filtered_extra + params[idx:]
    else:
        new_params = params + filtered_extra

    func.__signature__ = sig.replace(parameters=new_params)
    return func


_BASE_ARGS = {
    "autoscale": inspect.Parameter(
        "autoscale", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=True
    ),
    "figsize": inspect.Parameter(
        "figsize",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=tuple[float, float] | None,
        default=None,
    ),
    "title": inspect.Parameter(
        "title", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    "mask_color": inspect.Parameter(
        "mask_color", inspect.Parameter.KEYWORD_ONLY, annotation=str, default='black'
    ),
}

_CANVAS_ARGS = {
    "aspect": inspect.Parameter(
        "aspect",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=Literal['auto', 'equal', None],
        default=None,
    ),
    "coords": inspect.Parameter(
        "coords",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=list[str] | None,
        default=None,
    ),
    "errorbars": inspect.Parameter(
        "errorbars", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=True
    ),
    "grid": inspect.Parameter(
        "grid", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=False
    ),
    "ignore_size": inspect.Parameter(
        "ignore_size", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=False
    ),
    "legend": inspect.Parameter(
        "legend",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=bool | tuple[float, float],
        default=True,
    ),
    "xmin": inspect.Parameter(
        "xmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "xmax": inspect.Parameter(
        "xmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "ymin": inspect.Parameter(
        "ymin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "ymax": inspect.Parameter(
        "ymax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "logx": inspect.Parameter(
        "logx", inspect.Parameter.KEYWORD_ONLY, annotation=bool | None, default=None
    ),
    "logy": inspect.Parameter(
        "logy", inspect.Parameter.KEYWORD_ONLY, annotation=bool | None, default=None
    ),
    "xlabel": inspect.Parameter(
        "xlabel", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    "ylabel": inspect.Parameter(
        "ylabel", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    "norm": inspect.Parameter(
        "norm",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=Literal['linear', 'log', None],
        default=None,
    ),
    "vmin": inspect.Parameter(
        "vmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "vmax": inspect.Parameter(
        "vmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "scale": inspect.Parameter(
        "scale",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=dict[str, str] | None,
        default=None,
    ),
}

_COLOR_ARGS = {
    "cbar": inspect.Parameter(
        "cbar", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=True
    ),
    "nan_color": inspect.Parameter(
        "nan_color", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    "cmin": inspect.Parameter(
        "cmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "cmax": inspect.Parameter(
        "cmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "logc": inspect.Parameter(
        "logc", inspect.Parameter.KEYWORD_ONLY, annotation=bool | None, default=None
    ),
    "clabel": inspect.Parameter(
        "clabel", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    "norm": inspect.Parameter(
        "norm",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=Literal['linear', 'log', None],
        default=None,
    ),
    "vmin": inspect.Parameter(
        "vmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    "vmax": inspect.Parameter(
        "vmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
}

_THREE_D_ARGS = {
    "camera": inspect.Parameter(
        "camera", inspect.Parameter.KEYWORD_ONLY, annotation=object | None, default=None
    ),
}

_PLOT_ARGS_1D = _BASE_ARGS | _CANVAS_ARGS
_PLOT_ARGS_2D = _BASE_ARGS | _CANVAS_ARGS | _COLOR_ARGS
_PLOT_ARGS_3D = _BASE_ARGS | _COLOR_ARGS | _THREE_D_ARGS

_DOCSTRING_LIBRARY = {
    "aspect": "Aspect ratio for the axes.",
    "autoscale": (
        "Automatically adjust range of the axes and/or color scale every time the data "
        "changes if ``True``."
    ),
    "cbar": "Show colorbar in 2d plots if ``True``.",
    "coords": (
        "If supplied, use these coords instead of the input's dimension coordinates."
    ),
    "errorbars": "Show errorbars in 1d plots if ``True``.",
    "figsize": "The width and height of the figure, in inches.",
    "grid": "Show grid if ``True``.",
    "ignore_size": (
        "If ``True``, skip the check that prevents the rendering of very large data "
        "objects."
    ),
    "mask_color": "Color of masks in 1d plots.",
    "nan_color": "Color to use for NaN values in 2d plots.",
    "title": "The figure title.",
    "legend": (
        "Show legend if ``True``. If ``legend`` is a tuple, it should contain the "
        "``(x, y)`` coordinates of the legend's anchor point in axes coordinates."
    ),
    "xmin": "Lower limit for x-axis.",
    "xmax": "Upper limit for x-axis.",
    "ymin": "Lower limit for y-axis.",
    "ymax": "Upper limit for y-axis.",
    "logx": "If ``True``, use logarithmic scale for x-axis.",
    "logy": "If ``True``, use logarithmic scale for y-axis.",
    "logc": "If ``True``, use logarithmic scale for colorscale (2d plots only).",
    "xlabel": "Label for x-axis.",
    "ylabel": "Label for y-axis.",
    "clabel": "Label for colorscale (2d plots only).",
    "norm": (
        "Set to ``'log'`` for a logarithmic y-axis (1d plots) or logarithmic "
        "colorscale (2d plots). Legacy, prefer ``logy`` and ``logc`` instead."
    ),
    "vmin": (
        "Lower bound for data to be displayed (y-axis for 1d plots, colorscale for "
        "2d plots). Legacy, prefer ``ymin`` and ``cmin`` instead."
    ),
    "vmax": (
        "Upper bound for data to be displayed (y-axis for 1d plots, colorscale for "
        "2d plots). Legacy, prefer ``ymax`` and ``cmax`` instead."
    ),
    "scale": (
        "Change axis scaling between ``log`` and ``linear``. For example, specify "
        "``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension. "
        "Legacy, prefer ``logx`` and ``logy`` instead."
    ),
    "camera": "Initial camera configuration (position, target).",
}


def _with_plotting_params(args):
    def deco(func):
        out = _add_signature_params(func, args.values(), before_var_kw=True)
        doc = func.__doc__ or ''
        arg_strings = []
        for name in out.__signature__.parameters.keys():
            arg_doc = _DOCSTRING_LIBRARY.get(name, None)
            if arg_doc is not None:
                arg_strings.append(f"    {name}:\n        {arg_doc}")
        common_docstring = "\n".join(arg_strings)
        if "    **kwargs:" in doc:
            out.__doc__ = doc.replace(
                "    **kwargs:", common_docstring + "\n    **kwargs:"
            )
        else:
            out.__doc__ = doc + "\n" + common_docstring
        return out

    return deco


def with_1d_plot_params():
    return _with_plotting_params(_PLOT_ARGS_1D)


def with_2d_plot_params():
    return _with_plotting_params(_PLOT_ARGS_2D)


def with_3d_plot_params():
    return _with_plotting_params(_PLOT_ARGS_3D)
