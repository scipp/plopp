# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import inspect
from collections.abc import Callable, Sequence
from typing import Literal

import scipp as sc


def add_signature_params(
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


PLOT_COMMON_ARGS = [
    inspect.Parameter(
        "aspect",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=Literal['auto', 'equal', None],
        default=None,
    ),
    inspect.Parameter(
        "cbar", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=True
    ),
    inspect.Parameter(
        "coords",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=list[str] | None,
        default=None,
    ),
    inspect.Parameter(
        "errorbars", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=True
    ),
    inspect.Parameter(
        "figsize",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=tuple[float, float] | None,
        default=None,
    ),
    inspect.Parameter(
        "grid", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=False
    ),
    inspect.Parameter(
        "ignore_size", inspect.Parameter.KEYWORD_ONLY, annotation=bool, default=False
    ),
    inspect.Parameter(
        "mask_color", inspect.Parameter.KEYWORD_ONLY, annotation=str, default='black'
    ),
    inspect.Parameter(
        "nan_color", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    inspect.Parameter(
        "title", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    inspect.Parameter(
        "legend",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=bool | tuple[float, float],
        default=True,
    ),
    inspect.Parameter(
        "xmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "xmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "ymin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "ymax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "cmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "cmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "logx", inspect.Parameter.KEYWORD_ONLY, annotation=bool | None, default=None
    ),
    inspect.Parameter(
        "logy", inspect.Parameter.KEYWORD_ONLY, annotation=bool | None, default=None
    ),
    inspect.Parameter(
        "logc", inspect.Parameter.KEYWORD_ONLY, annotation=bool | None, default=None
    ),
    inspect.Parameter(
        "xlabel", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    inspect.Parameter(
        "ylabel", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    inspect.Parameter(
        "clabel", inspect.Parameter.KEYWORD_ONLY, annotation=str | None, default=None
    ),
    inspect.Parameter(
        "norm",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=Literal['linear', 'log', None],
        default=None,
    ),
    inspect.Parameter(
        "vmin",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "vmax",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=sc.Variable | float | None,
        default=None,
    ),
    inspect.Parameter(
        "scale",
        inspect.Parameter.KEYWORD_ONLY,
        annotation=dict[str, str] | None,
        default=None,
    ),
]

PLOT_COMMON_DOCSTRING = """aspect:
        Aspect ratio for the axes.
    cbar:
        Show colorbar in 2d plots if ``True``.
    coords:
        If supplied, use these coords instead of the input's dimension coordinates.
    errorbars:
        Show errorbars in 1d plots if ``True``.
    figsize:
        The width and height of the figure, in inches.
    grid:
        Show grid if ``True``.
    ignore_size:
        If ``True``, skip the check that prevents the rendering of very large data
        objects.
    mask_color:
        Color of masks in 1d plots.
    nan_color:
        Color to use for NaN values in 2d plots.
    title:
        The figure title.
    legend:
        Show legend if ``True``. If ``legend`` is a tuple, it should contain the
        ``(x, y)`` coordinates of the legend's anchor point in axes coordinates.
    xmin:
        Lower limit for x-axis.
    xmax:
        Upper limit for x-axis.
    ymin:
        Lower limit for y-axis.
    ymax:
        Upper limit for y-axis.
    cmin:
        Lower limit for colorscale (2d plots only).
    cmax:
        Upper limit for colorscale (2d plots only).
    logx:
        If ``True``, use logarithmic scale for x-axis.
    logy:
        If ``True``, use logarithmic scale for y-axis.
    logc:
        If ``True``, use logarithmic scale for colorscale (2d plots only).
    xlabel:
        Label for x-axis.
    ylabel:
        Label for y-axis.
    clabel:
        Label for colorscale (2d plots only).
    norm:
        Set to ``'log'`` for a logarithmic y-axis (1d plots) or logarithmic colorscale
        (2d plots). Legacy, prefer ``logy`` and ``logc`` instead.
    vmin:
        Lower bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymin`` and ``cmin`` instead.
    vmax:
        Upper bound for data to be displayed (y-axis for 1d plots, colorscale for
        2d plots). Legacy, prefer ``ymax`` and ``cmax`` instead.
    scale:
        Change axis scaling between ``log`` and ``linear``. For example, specify
        ``scale={'tof': 'log'}`` if you want log-scale for the ``tof`` dimension.
        Legacy, prefer ``logx`` and ``logy`` instead.
"""


def with_plotting_params():
    def deco(func):
        out = add_signature_params(func, PLOT_COMMON_ARGS, before_var_kw=True)
        doc = func.__doc__ or ''
        if "**kwargs:" in doc:
            out.__doc__ = doc.replace(
                "**kwargs:", PLOT_COMMON_DOCSTRING + "    **kwargs:"
            )
        else:
            out.__doc__ = doc + "\n" + PLOT_COMMON_DOCSTRING
        return out

    return deco
