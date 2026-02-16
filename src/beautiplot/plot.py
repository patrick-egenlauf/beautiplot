# Copyright 2020 Johannes Reiff modified by Patrick Egenlauf
# SPDX-License-Identifier: MIT
"""Plotting utilities."""

import math

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
    left: float = config.margin_threshold,
    right: float = config.margin_threshold,
    top: float = config.margin_threshold,
    bottom: float = config.margin_threshold,
    wspace: float = config.spacing_threshold,
    hspace: float = config.spacing_threshold,
    **kwargs: Any,
) -> tuple[mfigure.Figure, Any]:
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


def _union_bboxes(bboxes: list[mtrans.Bbox]) -> mtrans.Bbox | None:
    """Calculate the union of a list of bounding boxes."""
    if not bboxes:
        return None
    return mtrans.Bbox.union(bboxes)


def _get_axes_tight_bbox(
    axes: Sequence[matplotlib.axes.Axes], renderer: Any
) -> mtrans.Bbox | None:
    """Get the tight bounding box that contains all axes."""
    bboxes = []
    for ax in axes:
        bbox = ax.get_tightbbox(renderer)
        if bbox is not None:
            bboxes.append(bbox)
    return _union_bboxes(bboxes)


def _get_axes_pos_bbox(axes: Sequence[matplotlib.axes.Axes]) -> mtrans.Bbox | None:
    """Get the bounding box that contains the positions of the axes."""
    bboxes = [ax.get_position() for ax in axes]
    return _union_bboxes(bboxes)


def _bbox_center_dist_sq(b1: mtrans.Bbox, b2: mtrans.Bbox) -> float:
    """Calculate the distance between the centers of bounding boxes."""
    cx1 = 0.5 * (b1.x0 + b1.x1)
    cy1 = 0.5 * (b1.y0 + b1.y1)
    cx2 = 0.5 * (b2.x0 + b2.x1)
    cy2 = 0.5 * (b2.y0 + b2.y1)
    dx = cx1 - cx2
    dy = cy1 - cy2
    return dx * dx + dy * dy


def _check_wspace(
    grid: dict,
    rows: set,
    cols: set,
    renderer: Any,
    assigned_axes: dict,
) -> float | None:
    """Check for horizontal overlap between axes in adjacent columns."""
    max_w_overlap = -float('inf')
    found = False
    for r in sorted(rows):
        for c in sorted(cols):
            if (r, c) not in grid or (r, c + 1) not in grid:
                continue

            axes_left = list(grid[(r, c)] + assigned_axes.get((r, c), []))
            axes_right = list(grid[(r, c + 1)] + assigned_axes.get((r, c + 1), []))

            shared_axes = set(axes_left).intersection(axes_right)
            if shared_axes:
                axes_left = [ax for ax in axes_left if ax not in shared_axes]
                axes_right = [ax for ax in axes_right if ax not in shared_axes]

            bbox_left = _get_axes_tight_bbox(axes_left, renderer)
            bbox_right = _get_axes_tight_bbox(axes_right, renderer)

            if bbox_left is not None and bbox_right is not None:
                overlap = bbox_left.x1 - bbox_right.x0
                if overlap > max_w_overlap:
                    max_w_overlap = overlap
                found = True
    return max_w_overlap if found else None


def _check_hspace(
    grid: dict,
    rows: set,
    cols: set,
    renderer: Any,
    assigned_axes: dict,
) -> float | None:
    """Check for vertical overlap between axes in adjacent rows."""
    max_h_overlap = -float('inf')
    found = False
    for c in sorted(cols):
        for r in sorted(rows):
            if (r, c) not in grid or (r + 1, c) not in grid:
                continue

            axes_top = list(grid[(r, c)] + assigned_axes.get((r, c), []))
            axes_bottom = list(grid[(r + 1, c)] + assigned_axes.get((r + 1, c), []))

            shared_axes = set(axes_top).intersection(axes_bottom)
            if shared_axes:
                axes_top = [ax for ax in axes_top if ax not in shared_axes]
                axes_bottom = [ax for ax in axes_bottom if ax not in shared_axes]

            bbox_top = _get_axes_tight_bbox(axes_top, renderer)
            bbox_bottom = _get_axes_tight_bbox(axes_bottom, renderer)

            if bbox_top is not None and bbox_bottom is not None:
                overlap = bbox_bottom.y1 - bbox_top.y0
                if overlap > max_h_overlap:
                    max_h_overlap = overlap
                found = True
    return max_h_overlap if found else None


def _build_grid_from_axes(
    primary_axes: list[matplotlib.axes.Axes],
) -> tuple[dict[tuple[int, int], list[matplotlib.axes.Axes]], set, set]:
    """Build a grid mapping from subplot axes."""
    grid: dict[tuple[int, int], list[matplotlib.axes.Axes]] = {}
    rows = set()
    cols = set()

    for ax in primary_axes:
        ss = ax.get_subplotspec()
        if ss is not None:
            r_start = ss.rowspan.start
            r_stop = ss.rowspan.stop
            c_start = ss.colspan.start
            c_stop = ss.colspan.stop

            for r in range(r_start, r_stop):
                for c in range(c_start, c_stop):
                    if (r, c) not in grid:
                        grid[(r, c)] = []
                    grid[(r, c)].append(ax)
                    rows.add(r)
                    cols.add(c)

    return grid, rows, cols


def _find_overlapping_rows(
    ax_bbox: mtrans.Bbox,
    row_cells: dict[int, list[tuple[int, int]]],
    pos_grid: dict,
) -> set[int]:
    """Find rows that overlap with the colorbar."""
    def _interval_overlap(a0: float, a1: float, b0: float, b1: float) -> float:
        return max(0.0, min(a1, b1) - max(a0, b0))

    overlapping_rows: set[int] = set()
    for row, cells in row_cells.items():
        for cell in cells:
            cell_bbox = pos_grid.get(cell)
            if cell_bbox is None:
                continue
            if _interval_overlap(ax_bbox.y0, ax_bbox.y1, cell_bbox.y0, cell_bbox.y1) > 0:
                overlapping_rows.add(row)
                break
    return overlapping_rows if overlapping_rows else set(row_cells)


def _find_best_col(
    ax_bbox: mtrans.Bbox,
    col_cells: dict[int, list[tuple[int, int]]],
    pos_grid: dict,
) -> int | None:
    """Find the best column for the colorbar based on edge distance."""
    best_col = None
    best_edge_dist = float('inf')
    for col, cells in col_cells.items():
        edge_dist = float('inf')
        for cell in cells:
            cell_bbox = pos_grid.get(cell)
            if cell_bbox is None:
                continue
            edge_dist = min(edge_dist, abs(ax_bbox.x0 - cell_bbox.x1))
        if edge_dist < best_edge_dist:
            best_edge_dist = edge_dist
            best_col = col
    return best_col


def _assign_vertical_colorbar(
    ax: matplotlib.axes.Axes,
    ax_bbox: mtrans.Bbox,
    row_cells: dict[int, list[tuple[int, int]]],
    col_cells: dict[int, list[tuple[int, int]]],
    pos_grid: dict,
    grid: dict[tuple[int, int], list[matplotlib.axes.Axes]],
    assigned_axes: dict[tuple[int, int], list[matplotlib.axes.Axes]],
) -> bool:
    """Assign a vertical colorbar. Returns True if assigned."""
    overlapping_rows = _find_overlapping_rows(ax_bbox, row_cells, pos_grid)
    best_col = _find_best_col(ax_bbox, col_cells, pos_grid)

    if best_col is not None:
        for row in overlapping_rows:
            cell = (row, best_col)
            if cell in grid:
                assigned_axes.setdefault(cell, []).append(ax)
        return True
    return False


def _find_overlapping_cols(
    ax_bbox: mtrans.Bbox,
    col_cells: dict[int, list[tuple[int, int]]],
    pos_grid: dict,
) -> set[int]:
    """Find columns that overlap with the colorbar."""
    def _interval_overlap(a0: float, a1: float, b0: float, b1: float) -> float:
        return max(0.0, min(a1, b1) - max(a0, b0))

    overlapping_cols: set[int] = set()
    for col, cells in col_cells.items():
        for cell in cells:
            cell_bbox = pos_grid.get(cell)
            if cell_bbox is None:
                continue
            if _interval_overlap(ax_bbox.x0, ax_bbox.x1, cell_bbox.x0, cell_bbox.x1) > 0:
                overlapping_cols.add(col)
                break
    return overlapping_cols if overlapping_cols else set(col_cells)


def _find_best_row(
    ax_bbox: mtrans.Bbox,
    row_cells: dict[int, list[tuple[int, int]]],
    pos_grid: dict,
) -> int | None:
    """Find the best row for the colorbar based on edge distance."""
    best_row = None
    best_edge_dist = float('inf')
    for row, cells in row_cells.items():
        edge_dist = float('inf')
        for cell in cells:
            cell_bbox = pos_grid.get(cell)
            if cell_bbox is None:
                continue
            edge_dist = min(edge_dist, abs(ax_bbox.y0 - cell_bbox.y1))
        if edge_dist < best_edge_dist:
            best_edge_dist = edge_dist
            best_row = row
    return best_row


def _assign_horizontal_colorbar(
    ax: matplotlib.axes.Axes,
    ax_bbox: mtrans.Bbox,
    row_cells: dict[int, list[tuple[int, int]]],
    col_cells: dict[int, list[tuple[int, int]]],
    pos_grid: dict,
    grid: dict[tuple[int, int], list[matplotlib.axes.Axes]],
    assigned_axes: dict[tuple[int, int], list[matplotlib.axes.Axes]],
) -> bool:
    """Assign a horizontal colorbar. Returns True if assigned."""
    overlapping_cols = _find_overlapping_cols(ax_bbox, col_cells, pos_grid)
    best_row = _find_best_row(ax_bbox, row_cells, pos_grid)

    if best_row is not None:
        for col in overlapping_cols:
            cell = (best_row, col)
            if cell in grid:
                assigned_axes.setdefault(cell, []).append(ax)
        return True
    return False


def _assign_floating_axes(
    floating_axes: list[matplotlib.axes.Axes],
    grid: dict[tuple[int, int], list[matplotlib.axes.Axes]],
    pos_grid: dict,
) -> dict[tuple[int, int], list[matplotlib.axes.Axes]]:
    """Assign floating axes to grid cells.

    Colorbar axes are assigned by geometric overlap and proximity.
    Other floating axes fall back to nearest-cell assignment.
    """
    row_cells: dict[int, list[tuple[int, int]]] = {}
    col_cells: dict[int, list[tuple[int, int]]] = {}
    for (row, col) in grid:
        row_cells.setdefault(row, []).append((row, col))
        col_cells.setdefault(col, []).append((row, col))

    assigned_axes: dict[tuple[int, int], list[matplotlib.axes.Axes]] = {}
    for ax in floating_axes:
        ax_bbox = ax.get_position()
        is_colorbar_axis = (
            ax.get_label() == '<colorbar>'
            or getattr(ax, '_colorbar', None) is not None
        )

        if not is_colorbar_axis:
            _assign_nearest_cell(ax, ax_bbox, pos_grid, assigned_axes)
            continue

        width = ax_bbox.x1 - ax_bbox.x0
        height = ax_bbox.y1 - ax_bbox.y0
        if height >= width:
            if _assign_vertical_colorbar(
                ax, ax_bbox, row_cells, col_cells, pos_grid, grid, assigned_axes
                ):
                continue
        else:
            if _assign_horizontal_colorbar(
                ax, ax_bbox, row_cells, col_cells, pos_grid, grid, assigned_axes
                ):
                continue

        _assign_nearest_cell(ax, ax_bbox, pos_grid, assigned_axes)

    return assigned_axes


def _assign_nearest_cell(
    ax: matplotlib.axes.Axes,
    ax_bbox: mtrans.Bbox,
    pos_grid: dict,
    assigned_axes: dict[tuple[int, int], list[matplotlib.axes.Axes]],
) -> None:
    """Assign an axis to the nearest grid cell based on distance."""
    best_cell = None
    best_dist = float('inf')
    for cell, cell_bbox in pos_grid.items():
        if cell_bbox is not None:
            dist = _bbox_center_dist_sq(ax_bbox, cell_bbox)
            if dist < best_dist:
                best_dist = dist
                best_cell = cell
    if best_cell is not None:
        assigned_axes.setdefault(best_cell, []).append(ax)


def _suggest_spacing(fig: mfigure.Figure, renderer: Any, inch_to_bp: float) -> None:
    """Check for spacing issues and suggest adjustments."""
    primary_axes = [
        ax
        for ax in fig.axes
        if ax.get_visible() and ax.get_subplotspec() is not None and ax.get_label() != '<colorbar>'
    ]
    if len(primary_axes) <= 1:
        return

    grid, rows, cols = _build_grid_from_axes(primary_axes)

    if not grid:
        return

    pos_grid = {
        cell: _get_axes_pos_bbox(cell_axes)
        for cell, cell_axes in grid.items()
    }
    pos_grid = {cell: bbox for cell, bbox in pos_grid.items() if bbox is not None}

    floating_axes = [
        ax
        for ax in fig.axes
        if ax.get_visible() and ax not in primary_axes
    ]

    assigned_axes = _assign_floating_axes(floating_axes, grid, pos_grid)

    max_w_overlap = _check_wspace(grid, rows, cols, renderer, assigned_axes)
    max_h_overlap = _check_hspace(grid, rows, cols, renderer, assigned_axes)

    scale = inch_to_bp / fig.dpi
    tolerance = 1e-2

    if max_w_overlap is not None:
        w_adj = math.ceil(max_w_overlap * scale + config.spacing_threshold - tolerance)
        if abs(w_adj) > 0.5 and w_adj != 0:
            log(f'Suggestion: Adjust wspace: {w_adj:+.0f}')

    if max_h_overlap is not None:
        h_adj = math.ceil(max_h_overlap * scale + config.spacing_threshold - tolerance)
        if abs(h_adj) > 0.5 and h_adj != 0:
            log(f'Suggestion: Adjust hspace: {h_adj:+.0f}')


def _check_suptitle_overlap(fig: mfigure.Figure, renderer: Any, d_top: float) -> float:
    """Check if suptitle overlaps with subplots."""
    suptitle = getattr(fig, '_suptitle', None)
    if not (suptitle and suptitle.get_visible()):
        return d_top

    sup_bbox = suptitle.get_window_extent(renderer)
    max_overlap_bp = -float('inf')
    found_subplot = False

    for ax in fig.axes:
        if not ax.get_visible():
            continue
        ax_bbox = ax.get_tightbbox(renderer)

        if ax_bbox:
            found_subplot = True
            # ax_bbox from get_tightbbox is in pixels if used with
            # renderer
            overlap_pixels = ax_bbox.y1 - sup_bbox.y0
            current_overlap_bp = overlap_pixels / fig.dpi * 72.0
            if current_overlap_bp > max_overlap_bp:
                max_overlap_bp = current_overlap_bp

    if found_subplot:
        spacing_suggestion = max_overlap_bp + config.spacing_threshold
        d_top = spacing_suggestion

    return d_top


def _suggest_margins(fig: mfigure.Figure) -> None:
    """Check for margin and spacing issues and suggest adjustments."""
    try:
        if hasattr(fig.canvas, 'get_renderer'):
            renderer = fig.canvas.get_renderer()
        else:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()  # type: ignore[attr-defined]
    except Exception:
        return

    bbox = fig.get_tightbbox(renderer)
    if bbox is None:
        return

    width, height = fig.get_size_inches()
    inch_to_bp = 72.0

    d_left = -bbox.x0 * inch_to_bp + config.margin_threshold
    d_bottom = -bbox.y0 * inch_to_bp + config.margin_threshold
    d_right = (bbox.x1 - width) * inch_to_bp + config.margin_threshold
    d_top = (bbox.y1 - height) * inch_to_bp + config.margin_threshold

    d_top = _check_suptitle_overlap(fig, renderer, d_top)

    suggestions = []
    for name, val in [
        ('left', d_left),
        ('right', d_right),
        ('top', d_top),
        ('bottom', d_bottom),
    ]:
        val_rounded = math.ceil(val)
        if abs(val) > 0.5 and val_rounded != 0:
            suggestions.append(f'{name}: {val_rounded:+.0f}')

    if suggestions:
        log(f'Suggestion: Adjust margins: {", ".join(suggestions)}')

    _suggest_spacing(fig, renderer, inch_to_bp)


def save_figure(
    fig: mfigure.Figure,
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
        _suggest_margins(fig)
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
