"""Figure creation and saving utilities."""

from pathlib import Path
from typing import Any

import matplotlib.figure
import matplotlib.pyplot as plt

from ._diagnostics import suggest_margins
from .utils import log
from .._config import config


def newfig(
    width: float = 1.0,
    aspect: float = config.aspect,
    nrows: int = 1,
    ncols: int = 1,
    gridspec: bool = False,
    left: float = config.margin_threshold,
    right: float = config.margin_threshold,
    top: float = config.margin_threshold,
    bottom: float = config.margin_threshold,
    wspace: float = config.spacing_threshold,
    hspace: float = config.spacing_threshold,
    **kwargs: Any,
) -> tuple[matplotlib.figure.Figure, Any]:
    """Create a new figure with some default options.

    This function creates a new figure. You can specify margins (in bp)
    using `left`, `right`, `top`, and `bottom`. If you don't know the
    exact values, you can start with a guess. When you save the figure
    using [`save_figure`][beautiplot.plot.save_figure], `beautiplot`
    will analyze the layout and suggest adjustments if content is cut
    off or overlapping.

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
    fig: matplotlib.figure.Figure,
    file_path: str = 'plot.pdf',
    close: bool = True,
    silent: bool = False,
) -> None:
    """Save the figure to a file.

    This function saves the figure to the output path specified in the
    [`config.output_path`][beautiplot._config._Config.output_path]
    variable. You can use different file formats by changing the file
    extension in the `file_path` argument. For publication-quality
    figures, you should use `pdf` as the file format. In case of really
    large figures, you can still use `png` to save memory.

    This function also checks for layout issues (e.g. cut-off labels or
    overlapping subplots) and prints suggestions for adjusting margins
    and spacing to the terminal.

    Note:
        This function requires that the figure was created using
        [`newfig`][beautiplot.plot.newfig] to provide accurate margin
        and spacing suggestions.

    Note:
        Unlike [`tight_layout`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html),
        this function does not automatically adjust margins, as doing so
        while preserving axes dimensions would alter the figure size
        and effectively change the font size relative to the document.
        Instead, it provides specific suggestions for manual adjustment
        to ensure the figure maintains its exact intended dimensions.

    Args:
        fig: The figure to save.
        file_path: The path to save the figure to.
        close: Whether to close the figure after saving.
        silent: Whether to suppress log messages. This does affect
            suggestions for margin and spacing adjustments as well.
    """
    file_ext = Path(file_path).suffix.upper().lstrip('.')
    if not silent:
        log(f'Writing figure to {file_ext}...')

    path = Path(config.output_path) / Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(str(path))
    if not silent:
        suggest_margins(fig)
    if close:
        plt.close(fig)
