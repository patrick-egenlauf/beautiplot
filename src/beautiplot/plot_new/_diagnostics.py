"""Layout diagnostics and suggestions."""

import math
from collections.abc import Sequence
from typing import Any

import matplotlib.axes
import matplotlib.figure
import matplotlib.transforms as mtrans

from .utils import log
from .._config import config


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
            if (
                _interval_overlap(ax_bbox.y0, ax_bbox.y1, cell_bbox.y0, cell_bbox.y1)
                > 0
            ):
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
            if (
                _interval_overlap(ax_bbox.x0, ax_bbox.x1, cell_bbox.x0, cell_bbox.x1)
                > 0
            ):
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
    for row, col in grid:
        row_cells.setdefault(row, []).append((row, col))
        col_cells.setdefault(col, []).append((row, col))

    assigned_axes: dict[tuple[int, int], list[matplotlib.axes.Axes]] = {}
    for ax in floating_axes:
        ax_bbox = ax.get_position()
        is_colorbar_axis = (
            ax.get_label() == '<colorbar>' or getattr(ax, '_colorbar', None) is not None
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


def _suggest_spacing(
    fig: matplotlib.figure.Figure, renderer: Any, inch_to_bp: float
) -> None:
    """Check for spacing issues and suggest adjustments."""
    primary_axes = [
        ax
        for ax in fig.axes
        if ax.get_visible()
        and ax.get_subplotspec() is not None
        and ax.get_label() != '<colorbar>'
    ]
    if len(primary_axes) <= 1:
        return

    grid, rows, cols = _build_grid_from_axes(primary_axes)

    if not grid:
        return

    pos_grid = {cell: _get_axes_pos_bbox(cell_axes) for cell, cell_axes in grid.items()}
    pos_grid = {cell: bbox for cell, bbox in pos_grid.items() if bbox is not None}

    floating_axes = [
        ax for ax in fig.axes if ax.get_visible() and ax not in primary_axes
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


def _check_suptitle_overlap(
    fig: matplotlib.figure.Figure, renderer: Any, d_top: float
) -> float:
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


def suggest_margins(fig: matplotlib.figure.Figure) -> None:
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
