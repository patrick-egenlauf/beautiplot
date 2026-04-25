"""Layout and axes adjustment utilities."""

from collections.abc import Sequence
from typing import Literal

import matplotlib.axes
import numpy as np


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
