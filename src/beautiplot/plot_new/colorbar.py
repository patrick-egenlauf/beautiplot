"""Colorbar utilities."""

from collections.abc import Sequence
from typing import Any, Literal

import matplotlib.axes
import matplotlib.colorbar
import matplotlib.colors as mcolors
import matplotlib.figure
import matplotlib.image
import matplotlib.pyplot as plt
import numpy as np

from .layout import fig_hspace, fig_wspace
from .utils import fmt_num
from .._config import config


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
        [discretized colorbar
        tutorial](../../../tutorials/discretized_colorbar.md).
    """
    cmap = plt.get_cmap(colormap, np.max(data) - np.min(data) + 1)
    vmin = np.min(data) - 0.5
    vmax = np.max(data) + 0.5
    ticks = np.arange(np.min(data), np.max(data) + 1)
    return cmap, vmin, vmax, ticks


def cbar_beside(
    fig: matplotlib.figure.Figure,
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
    fig: matplotlib.figure.Figure,
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
        [discretized colorbar
        tutorial](../../../tutorials/discretized_colorbar.md).
    """
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
