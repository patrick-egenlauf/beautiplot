"""Plotting elements (text, markers, arrows, legend, images)."""

from typing import Any, Literal

import matplotlib.axes
import matplotlib.colors as mcolors
import matplotlib.figure
import matplotlib.image
import matplotlib.legend
import matplotlib.patches
import matplotlib.transforms as mtrans
import numpy as np

from .._config import config


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
    x: int | float | np.ndarray | list[int | float],
    y: int | float | np.ndarray | list[int | float],
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
        See the [discretized colorbar
        tutorial](../../../tutorials/discretized_colorbar.md).
    """
    ax.plot(x, y, marker=marker, ms=ms, mec=mec, mew=mew, ls=ls, **kwargs)


def add_arrow(
    fig_or_ax: matplotlib.figure.Figure | matplotlib.axes.Axes,
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
    if isinstance(fig_or_ax, matplotlib.figure.FigureBase):
        kwargs.setdefault('transform', fig_or_ax.transFigure)

    fig_or_ax.add_artist(matplotlib.patches.FancyArrowPatch(from_pos, to_pos, **kwargs))


def legend(
    fig_or_ax: matplotlib.axes.Axes | matplotlib.figure.Figure,
    *args: Any,
    **kwargs: Any,
) -> matplotlib.legend.Legend:
    """Create a legend with some default options.

    Args:
        fig_or_ax: The figure or axes to add the legend to.
        *args: Additional arguments to pass to `ax.legend`.
        **kwargs: Additional keyword arguments to pass to `ax.legend`.

    Returns:
        The legend.
    """
    return fig_or_ax.legend(*args, **(config.legend_setup | kwargs))
