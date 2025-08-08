# Copyright 2020 Johannes Reiff modified by Patrick Egenlauf
# SPDX-License-Identifier: MIT
"""Plotting utilities."""

import matplotlib
import matplotlib.axes

matplotlib.use('pgf')

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import matplotlib.colors as mcolors
import matplotlib.figure as mfigure
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import numpy as np

from ._config import config


def log(msg: str, *args: str | int | float, **kwargs: str | int | float) -> None:
    """Log a message.

    Args:
        msg: The message to log.
        *args: Additional arguments to format the message.
        **kwargs: Additional keyword arguments to format the message.
    """
    print('  ' + msg.format(*args, **kwargs))


def fmt_num(num: int | float | np.integer | np.floating, fmt: str = 'g') -> str:
    """Format a number as a LaTeX number.

    Args:
        num: The number to format.
        fmt: The format string.

    Returns:
        The formatted number.
    """
    return rf'\num{{{num:{fmt}}}}'


def newfig(
    width: float = 1.0,
    aspect: float = config.aspect,
    nrows: int = 1,
    ncols: int = 1,
    gridspec: bool = False,
    left: float = 1,
    right: float = 1,
    top: float = 1,
    bottom: float = 1,
    wspace: float = 6,
    hspace: float = 6,
    **kwargs: Any,
) -> tuple[mfigure.Figure, Any]:
    """Create a new figure with some default options.

    This function creates a new figure. At first, you need to estimate
    the margins, but you can adjust them later as needed. If you do not
    specify any margins, the figure will be trimmed to the axes, and
    tick labels or axis labels won't be visible.

    Args:
        width: The width of the figure in textwidths. The given width is
            multiplied by the width specified in
            [`config.width`][beautiplot._config._Config.width].
        aspect: The aspect ratio of the axes.
        nrows: The number of rows of axes.
        ncols: The number of columns of axes.
        gridspec: Whether to use a gridspec.
        left: The left margin in big points (bp).
        right: The right margin in bp.
        top: The top margin in bp.
        bottom: The bottom margin in bp.
        wspace: The width space between axes in bp.
        hspace: The height space between axes in bp.
        **kwargs: Additional keyword arguments to pass to `plt.figure`.

    Returns:
        A tuple containing the created figure and axes or gridspec.
    """
    if 'gridspec_kw' in kwargs:
        raise ValueError('gridspec_kw is not supported')
    kwargs.setdefault('dpi', config.dpi)

    bp = config.bp
    width *= config.width
    left, right, top, bottom = left * bp, right * bp, top * bp, bottom * bp
    wspace, hspace = wspace * bp, hspace * bp

    axes_width = (width - left - right - wspace * (ncols - 1)) / ncols
    axes_height = axes_width / aspect
    height = axes_height * nrows + top + bottom + hspace * (nrows - 1)

    if gridspec:
        gs_kwargs = {
            name: kwargs.pop(name, None) for name in ('width_ratios', 'height_ratios')
        }
        fig = plt.figure(figsize=(width, height), **kwargs)
        axes_or_gs = fig.add_gridspec(nrows, ncols, **gs_kwargs)
    else:
        fig, axes_or_gs = plt.subplots(
            figsize=(width, height), nrows=nrows, ncols=ncols, **kwargs
        )

    fig.subplots_adjust(
        left=left / width,
        right=1 - right / width,
        top=1 - top / height,
        bottom=bottom / height,
        wspace=wspace / axes_width,
        hspace=hspace / axes_height,
    )

    return fig, axes_or_gs


def save_figure(
    fig: mfigure.Figure, file_path: str = 'plot.pdf', close: bool = True
) -> None:
    """Save the figure to a file.

    This function saves the figure to the output path specified in the
    [`config.output_path`][beautiplot._config._Config.output_path]
    variable. You can use different file formats by changing the file
    extension in the `file_path` argument. For publication-quality
    figures, you should use `pdf` as the file format. In case of really
    large figures, you can still use `png` to save memory.

    Args:
        fig: The figure to save.
        file_path: The path to save the figure to.
        close: Whether to close the figure after saving.
    """
    file_ext = Path(file_path).suffix.upper().lstrip('.')
    log(f'Writing figure to {file_ext}...')

    path = Path(config.output_path) / Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(str(path))
    if close:
        plt.close(fig)


def extent(
    data: dict[str, np.ndarray], x: str = 'x', y: str = 'y'
) -> tuple[float, float, float, float]:
    """Calculate the extent of the data.

    Args:
        data: The data to calculate the extent for.
        x: The x-axis label.
        y: The y-axis label.

    Returns:
        The extent of the data as a tuple of (left, right, bottom, top).

    Example:
        See the tutorial on how to create a
        [shared colorbar](../../../tutorials/shared_colorbar.md).
    """
    return tuple(data[x].reshape(-1)[[0, -1]]) + tuple(data[y].reshape(-1)[[0, -1]])


def fig_wspace(ax: matplotlib.axes.Axes) -> float:
    """Calculate the width space between axes.

    Args:
        ax: The axes to calculate the width space for.

    Returns:
        float: The width space between axes.
    """
    if ax.figure is not None:
        sp = ax.figure.subplotpars
    else:
        raise Exception('Figure not found for axes')
    gs = ax.get_gridspec()
    if gs is None:
        raise Exception('Gridspec not found for axes')
    return sp.wspace * (sp.right - sp.left) / (gs.ncols + sp.wspace * (gs.ncols - 1))


def fig_hspace(ax: matplotlib.axes.Axes) -> float:
    """Calculate the height space between axes.

    Args:
        ax: The axes to calculate the height space for.

    Returns:
        float: The height space between axes.
    """
    if ax.figure is not None:
        sp = ax.figure.subplotpars
    else:
        raise Exception('Figure not found for axes')
    gs = ax.get_gridspec()
    if gs is None:
        raise Exception('Gridspec not found for axes')
    return sp.hspace * (sp.top - sp.bottom) / (gs.nrows + sp.hspace * (gs.nrows - 1))


def subfig_label(
    ax: matplotlib.axes.Axes,
    idx: int | str,
    ha: Literal['left', 'center', 'right'],
    x: float,
    dx: float,
    va: Literal['top', 'center', 'bottom'],
    y: float,
    dy: float,
    **kwargs: Any,
) -> None:
    """Add a label to a subplot.

    Args:
        ax (matplotlib.axes.Axes): The axes to add the label to.
        idx: The index of the subplot.
        ha: The horizontal alignment.
        x: The x-coordinate of the label. Here, 0.0 is left and 1.0 is
            right of the axes.
        dx: The x-offset of the label. Negative values move the label
            left, positive values move it right.
        va: The vertical alignment.
        y: The y-coordinate of the label. Here, 0.0 is bottom and 1.0 is
            top of the axes.
        dy: The y-offset of the label. Negative values move the label
            down, positive values move it up.
        **kwargs: Additional keyword arguments to pass to `ax.text`.

    Example:
        See the tutorial on how to create a
        [shared colorbar](../../../tutorials/shared_colorbar.md).
    """
    label = chr(ord('a') + idx) if isinstance(idx, int) else str(idx)
    text(ax, ha, x, dx, va, y, dy, rf'\textbf{{({label})}}', **kwargs)


def auto_xlim_aspect_1(ax: matplotlib.axes.Axes, offset: float = 0.0) -> None:
    """Set the x-axis limits to maintain an aspect ratio of 1.

    This is useful whenever you want that one unit on the x-axis is the
    same length as one unit on the y-axis.

    Args:
        ax: The axes to set the limits for.
        offset: The offset to add to the limits.

    Example:
        See the
        [`auto_xlim_aspect_1`](../../../tutorials/auto_xlim_aspect_1.md)
        example in the tutorial section.
    """
    y_min, y_max = ax.get_ylim()
    width, height = np.abs(ax.get_window_extent().size)
    dx = width / height * (y_max - y_min)
    ax.set_xlim(np.array([-0.5, +0.5]) * dx + offset)


def common_lims(
    axis: Literal['x', 'y'],
    axes: Sequence[matplotlib.axes.Axes] | np.ndarray,
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    """Set common limits for a list of axes.

    Args:
        axis: The axis to set the limits for ('x' or 'y').
        axes: The list of axes to set the limits for.
        vmin: The minimum limit.
        vmax: The maximum limit.

    Example:
        See the
        [common limits example](../../../tutorials/common_lims.md).
    """
    if isinstance(axes, np.ndarray):
        axes = axes.ravel()
    clims = np.array([getattr(ax, f'get_{axis}lim')() for ax in axes])
    vmin = clims.min() if vmin is None else vmin
    vmax = clims.max() if vmax is None else vmax

    for ax in axes:
        getattr(ax, f'set_{axis}lim')(vmin, vmax)


def imshow(
    ax: matplotlib.axes.Axes,
    data: np.ndarray,
    extent: tuple[float, float, float, float],
    cmap: str | mcolors.Colormap = config.cmap,
    interp: bool | str = True,
    **kwargs: Any,
) -> matplotlib.image.AxesImage:
    """Display an image on the axes.

    Args:
        ax: The axes to display the image on.
        data: The image data.
        extent: The extent of the image.
        cmap: The colormap to use.
        interp: Whether to interpolate the image.
        **kwargs: Additional keyword arguments to pass to `ax.imshow`.

    Returns:
        matplotlib.image.AxesImage: The image.

    Example:
        See the tutorial on how to create a
        [shared colorbar](../../../tutorials/shared_colorbar.md).
    """
    interpolation = 'spline16' if interp is True else interp if interp else None
    return ax.imshow(
        data,
        cmap=cmap,
        aspect='auto',
        interpolation=interpolation,
        origin='lower',
        extent=extent,
        **kwargs,
    )


def markers(
    ax: matplotlib.axes.Axes,
    x: int | float | np.ndarray | Sequence[int | float],
    y: int | float | np.ndarray | Sequence[int | float],
    marker: str = 'o',
    ms: int = 8,
    mec: str = 'white',
    mew: float = 0.5,
    ls: str = 'None',
    **kwargs: Any,
) -> None:
    """Plot markers on the axes.

    Args:
        ax: The axes to plot on.
        x: The x-coordinates of the markers.
        y: The y-coordinates of the markers.
        marker: The marker style.
        ms: The marker size.
        mec: The marker edge color.
        mew: The marker edge width.
        ls: The line style.
        **kwargs: Additional keyword arguments to pass to `ax.plot`.

    Example:
        See the
        [discretized colorbar tutorial](../../../tutorials/discretized_colorbar.md).
    """  # noqa: W505
    ax.plot(x, y, marker=marker, ms=ms, mec=mec, mew=mew, ls=ls, **kwargs)


def discretize_colormap(
    data: np.ndarray | Sequence[int],
    colormap: mcolors.Colormap | str = config.cmap.name,
) -> tuple[mcolors.Colormap, float, float, np.ndarray]:
    """Create a discrete colormap from the data.

    This function can be used to create a colormap that is
    discretized according to the unique values in the data. It can be
    used to create a colormap for categorical data, e.g., for regions or
    clusters in a 2D grid. By default, the ticklabels of the colorbar
    will be integers from the minimum to the maximum value of the data,
    but this can be customized by adjusting the returned `ticks` array
    or by setting custom tick labels on the colorbar.

    Args:
        data: The data to create the colormap from. It should be a
            1D array or a sequence of integers representing the
            categories or regions. The colormap will be discretized
            according to the difference between the maximum and
            minimum values of the data.
        colormap: The colormap to use. If a `Colormap` object is
            provided, it will be returned with adjusted ticks according
            to the data's minimum and maximum values. Otherwise, the
            name of a colormap known to Matplotlib can be provided as a
            string, which will be resampled by the difference between
            the minimum and maximum values of the data to create a
            discrete colormap.

    Returns:
        tuple: A tuple containing:

            - cmap: The discrete colormap.
            - vmin: The minimum value of the data.
            - vmax: The maximum value of the data.
            - ticks: The ticks of the colormap.

    Example:
        See the
        [discretized colorbar tutorial](../../../tutorials/discretized_colorbar.md).
    """  # noqa: W505
    cmap = plt.get_cmap(colormap, np.max(data) - np.min(data) + 1)
    vmin = np.min(data) - 0.5
    vmax = np.max(data) + 0.5
    ticks = np.arange(np.min(data), np.max(data) + 1)
    return cmap, vmin, vmax, ticks


def cbar_beside(
    fig: mfigure.Figure,
    axes: matplotlib.axes.Axes | Sequence[matplotlib.axes.Axes],
    aximg: matplotlib.image.AxesImage,
    dx: float | None = None,
    **kwargs: Any,
) -> tuple[matplotlib.colorbar.Colorbar, matplotlib.axes.Axes]:
    """Add a colorbar beside the axes.

    Args:
        fig: The figure to add the colorbar to.
        axes: The axes to add the colorbar beside.
        aximg: The image to create the colorbar for.
        dx: The horizontal spacing between the axes and the colorbar. If
            not given, the default spacing is used.
        **kwargs: Additional keyword arguments to pass to
            `fig.colorbar`.

    Returns:
        A tuple containing the created colorbar and the colorbar axes.

    Example:
        See the tutorial on how to create a
        [shared colorbar](../../../tutorials/shared_colorbar.md).
    """
    if isinstance(axes, np.ndarray):
        axes = axes.ravel()
    ax_list = axes if isinstance(axes, list | tuple | np.ndarray) else [axes]
    pos = [ax_list[idx].get_position() for idx in (0, -1)]
    dx = fig_wspace(ax_list[0]) if dx is None else dx
    cax = fig.add_axes((
        pos[1].xmax + dx,
        pos[1].ymin,
        config.colorbar_width / fig.get_figwidth(),
        pos[0].ymax - pos[1].ymin,
    ))
    cbar = fig.colorbar(aximg, cax=cax, orientation='vertical', **kwargs)
    return cbar, cax


def cbar_above(
    fig: mfigure.Figure,
    axes: matplotlib.axes.Axes | Sequence[matplotlib.axes.Axes] | np.ndarray,
    aximg: matplotlib.image.AxesImage,
    dy: float | None = None,
    **kwargs: Any,
) -> tuple[matplotlib.colorbar.Colorbar, matplotlib.axes.Axes]:
    """Add a colorbar above the axes.

    Args:
        fig: The figure to add the colorbar to.
        axes: The axes to add the colorbar above.
        aximg: The image to create the colorbar for.
        dy: The vertical spacing between the axes and the colorbar. If
            not given, the default spacing is used.
        **kwargs: Additional keyword arguments to pass to
            `fig.colorbar`.

    Returns:
        A tuple containing the created colorbar and the colorbar axes.

    Example:
        See the
        [discretized colorbar tutorial](../../../tutorials/discretized_colorbar.md).
    """  # noqa: W505
    if isinstance(axes, np.ndarray):
        axes = axes.ravel()
    ax_list = axes if isinstance(axes, list | tuple | np.ndarray) else [axes]
    pos = [ax_list[idx].get_position() for idx in (0, -1)]
    dy = fig_hspace(ax_list[0]) if dy is None else dy
    cax = fig.add_axes((
        pos[0].xmin,
        pos[0].ymax + dy,
        pos[1].xmax - pos[0].xmin,
        config.colorbar_width / fig.get_figheight(),
    ))
    cbar = fig.colorbar(aximg, cax=cax, orientation='horizontal', **kwargs)
    cax.xaxis.set_ticks_position('top')
    cax.xaxis.set_label_position('top')
    return cbar, cax


def cbar_minmax_labels(
    cbar: matplotlib.colorbar.Colorbar,
    labels: Sequence[str] | None = None,
    fmt: str = 'g',
) -> None:
    """Set ticks of a colorbar to the min and max values of the data.

    Args:
        cbar: The colorbar to set the ticks for.
        labels: The labels for the ticks. If not given, the minimum and
            maximum values of the data are used.
        fmt: The format string for the labels. Default is 'g'.

    Example:
        See the tutorial on how to
        [add an arrow to a plot](../../../tutorials/add_arrow.md).
    """
    halignments: tuple[Literal['left', 'right'], Literal['left', 'right']] = (
        'left',
        'right',
    )
    valignments: tuple[Literal['bottom', 'top'], Literal['bottom', 'top']] = (
        'bottom',
        'top',
    )
    labels = labels or [fmt_num(x, fmt) for x in cbar.mappable.get_clim()]
    cbar.set_ticks(cbar.mappable.get_clim(), labels=labels)
    if cbar.orientation == 'horizontal':
        for halign, label in zip(
            halignments, cbar.ax.xaxis.get_ticklabels(), strict=True
        ):
            label.set_horizontalalignment(halign)
    elif cbar.orientation == 'vertical':
        for valign, label in zip(
            valignments, cbar.ax.yaxis.get_ticklabels(), strict=True
        ):
            label.set_verticalalignment(valign)


def legend(
    ax: matplotlib.axes.Axes, *args: Any, **kwargs: Any
) -> matplotlib.legend.Legend:
    """Create a legend with some default options.

    Args:
        ax: The axes to add the legend to.
        *args: Additional arguments to pass to `ax.legend`.
        **kwargs: Additional keyword arguments to pass to `ax.legend`.

    Returns:
        The legend.
    """
    return ax.legend(*args, **(config.legend_setup | kwargs))


def text(
    ax: matplotlib.axes.Axes,
    ha: Literal['left', 'center', 'right'],
    x: float,
    dx: float,
    va: Literal['top', 'center', 'bottom'],
    y: float,
    dy: float,
    txt: str,
    **kwargs: Any,
) -> None:
    """Add text to an axes with relative coordinates.

    Args:
        ax: The axes to plot on.
        ha: The horizontal alignment.
        x: The x-coordinate of the text. Here, 0.0 is left and 1.0 is
            right of the axes.
        dx: The x-offset of the text.
        va: The vertical alignment.
        y: The y-coordinate of the text. Here, 0.0 is bottom and 1.0 is
            top of the axes.
        dy: The y-offset of the text.
        txt: The text to add.
        **kwargs: Additional keyword arguments to pass to `ax.text`.

    Example:
        See the tutorial on how to
        [add text to a plot](../../../tutorials/add_arrow.md).
    """
    bp = config.bp
    if ax.figure is None:
        raise Exception('Figure not found for axes')
    trans = ax.transAxes + mtrans.ScaledTranslation(
        dx * bp, dy * bp, ax.figure.dpi_scale_trans
    )
    ax.text(x, y, txt, transform=trans, ha=ha, va=va, **kwargs)


def add_arrow(
    fig_or_ax: mfigure.Figure | matplotlib.axes.Axes,
    from_pos: tuple[float, float],
    to_pos: tuple[float, float],
    **kwargs: Any,
) -> None:
    """Add an arrow to a figure or axes.

    Args:
        fig_or_ax: The figure or axes to plot on.
        from_pos: The start position of the arrow. The coordinates
            should be in normalized (0 to 1) coordinates relative to the
            axes, where (0, 0) is the bottom left and (1, 1) is the top
            right.
        to_pos: The end position of the arrow. As with `from_pos`, the
            coordinates should be in normalized coordinates relative to
            the axes.
        **kwargs: Additional keyword arguments to pass to
            `matplotlib.patches.FancyArrowPatch`.

    Example:
        See the tutorial on how to
        [add an arrow to a plot](../../../tutorials/add_arrow.md).
    """
    kwargs.setdefault('color', 'k')
    kwargs.setdefault('lw', 1.5)
    kwargs.setdefault(
        'arrowstyle', 'fancy, head_width=6, head_length=6, tail_width=1e-12'
    )
    if isinstance(fig_or_ax, mfigure.FigureBase):
        kwargs.setdefault('transform', fig_or_ax.transFigure)

    fig_or_ax.add_artist(mpatches.FancyArrowPatch(from_pos, to_pos, **kwargs))
