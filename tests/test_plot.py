import io
from pathlib import Path
from unittest.mock import patch

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import numpy as np
from matplotlib.colors import to_rgba
from pytest import approx

import beautiplot.plot as bp
from beautiplot import config


def test_newfig_defaults() -> None:
    fig, axes = bp.newfig()
    assert isinstance(fig, plt.Figure), 'fig is not a matplotlib Figure'
    assert isinstance(axes, plt.Axes), 'axes is not a matplotlib Axes'
    assert len(fig.axes) == 1, 'number of axes is not 1'
    assert fig.get_figwidth() == approx(
        config.width
    ), 'fig width is not the default width'
    _bp = config.bp
    assert fig.get_figheight() == approx(
        (config.width - 2 * _bp) / config.aspect + 2 * _bp
    ), 'fig height is not the default height'
    assert fig.get_dpi() == config.dpi, 'fig dpi is not the default dpi'
    assert fig.subplotpars.left == approx(
        _bp / fig.get_figwidth()
    ), 'left margin is not the default margin'
    assert fig.subplotpars.right == approx(
        1 - _bp / fig.get_figwidth()
    ), 'right margin is not the default margin'
    assert fig.subplotpars.top == approx(
        1 - _bp / fig.get_figheight()
    ), 'top margin is not the default margin'
    assert fig.subplotpars.bottom == approx(
        _bp / fig.get_figheight()
    ), 'bottom margin is not the default margin'
    plt.close(fig)


def test_newfig_custom_size() -> None:
    fig, axes = bp.newfig(width=0.5, aspect=1.0)
    assert isinstance(fig, plt.Figure)
    assert isinstance(axes, plt.Axes)
    assert fig.get_figwidth() == 0.5 * config.width
    assert fig.get_figheight() == 0.5 * config.width / 1.0
    plt.close(fig)


def test_newfig_gridspec() -> None:
    fig, gs = bp.newfig(nrows=2, ncols=2, gridspec=True)
    assert isinstance(fig, plt.Figure)
    assert isinstance(gs, matplotlib.gridspec.GridSpec)
    assert gs.get_geometry() == (2, 2)
    plt.close(fig)


def test_newfig_margins() -> None:
    fig, axes = bp.newfig(left=2, right=2, top=2, bottom=2)
    assert isinstance(fig, plt.Figure)
    assert isinstance(axes, plt.Axes)
    assert fig.subplotpars.left == 2 * config.bp / fig.get_figwidth()
    assert fig.subplotpars.right == 1 - 2 * config.bp / fig.get_figwidth()
    assert fig.subplotpars.top == 1 - 2 * config.bp / fig.get_figheight()
    assert fig.subplotpars.bottom == 2 * config.bp / fig.get_figheight()
    plt.close(fig)


def test_newfig_spacing() -> None:
    fig, axes = bp.newfig(nrows=2, ncols=2, wspace=10, hspace=15)
    assert isinstance(fig, plt.Figure)
    assert isinstance(axes, np.ndarray)
    assert [isinstance(ax, plt.Axes) for ax in axes]
    _bp = config.bp
    assert fig.subplotpars.wspace == approx(
        10 * _bp / ((fig.get_figwidth() - 12 * _bp) / len(axes[0]))
    )
    assert fig.subplotpars.hspace == approx(
        15 * _bp / (((fig.get_figwidth() - 12 * _bp) / len(axes[0])) / config.aspect)
    )
    plt.close(fig)


def test_newfig_kwargs() -> None:
    fig, axes = bp.newfig(facecolor='red')
    rgba = to_rgba('red')
    assert isinstance(fig, plt.Figure)
    assert isinstance(axes, plt.Axes)
    assert fig.get_facecolor() == rgba
    plt.close(fig)


def test_fmt_num_default_format() -> None:
    assert bp.fmt_num(1234.5678) == r'\num{1234.57}'
    assert bp.fmt_num(0.0001234) == r'\num{0.0001234}'


def test_fmt_num_custom_format() -> None:
    assert bp.fmt_num(1234.5678, 'e') == r'\num{1.234568e+03}'
    assert bp.fmt_num(0.0001234, '.2f') == r'\num{0.00}'
    assert bp.fmt_num(1234.5678, '.1f') == r'\num{1234.6}'


def test_save_figure_default_path() -> None:
    fig, _ = plt.subplots()
    with (
        patch.object(Path, 'mkdir') as mock_mkdir,
        patch.object(plt.Figure, 'savefig') as mock_savefig,
        patch('matplotlib.pyplot.close') as mock_close,
        patch('sys.stdout', new=io.StringIO()) as mock_log,
        patch('beautiplot.plot._suggest_margins'),  # Mock suggestions
    ):
        bp.save_figure(fig)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert mock_log.getvalue().strip() == 'Writing figure to PDF...'
        mock_savefig.assert_called_once_with('plot.pdf')
        mock_close.assert_called_once_with(fig)
    plt.close(fig)


def test_save_figure_custom_path() -> None:
    fig, _ = plt.subplots()
    custom_path = 'custom_plot.pdf'
    with (
        patch.object(Path, 'mkdir') as mock_mkdir,
        patch.object(plt.Figure, 'savefig') as mock_savefig,
        patch('matplotlib.pyplot.close') as mock_close,
        patch('sys.stdout', new=io.StringIO()) as mock_log,
        patch('beautiplot.plot._suggest_margins'),  # Mock suggestions
    ):
        bp.save_figure(fig, file_path=custom_path)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert mock_log.getvalue().strip() == 'Writing figure to PDF...'
        mock_savefig.assert_called_once_with(custom_path)
        mock_close.assert_called_once_with(fig)
    plt.close(fig)


def test_save_figure_no_close() -> None:
    fig, _ = plt.subplots()
    with (
        patch.object(Path, 'mkdir') as mock_mkdir,
        patch.object(plt.Figure, 'savefig') as mock_savefig,
        patch('matplotlib.pyplot.close') as mock_close,
        patch('sys.stdout', new=io.StringIO()) as mock_log,
        patch('beautiplot.plot._suggest_margins'),  # Mock suggestions
    ):
        bp.save_figure(fig, close=False)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert mock_log.getvalue().strip() == 'Writing figure to PDF...'
        mock_savefig.assert_called_once_with('plot.pdf')
        mock_close.assert_not_called()
    plt.close(fig)


def test_log_message() -> None:
    with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
        bp.log('Test message')
        assert mock_stdout.getvalue().strip() == 'Test message'


def test_log_message_with_args() -> None:
    with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
        bp.log('Test message with args: {}', 123)
        assert mock_stdout.getvalue().strip() == 'Test message with args: 123'


def test_log_message_with_kwargs() -> None:
    with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
        bp.log('Test message with kwargs: {value}', value=456)
        assert mock_stdout.getvalue().strip() == 'Test message with kwargs: 456'


def test_extent_default_labels() -> None:
    data = {
        'x': np.array([[1, 2, 3], [4, 5, 6]]),
        'y': np.array([[7, 8, 9], [10, 11, 12]]),
    }
    result = bp.extent(data)
    assert result == (1, 6, 7, 12), f'Expected (1, 6, 7, 12) but got {result}'


def test_extent_custom_labels() -> None:
    data = {
        'a': np.array([[1, 2, 3], [4, 5, 6]]),
        'b': np.array([[7, 8, 9], [10, 11, 12]]),
    }
    result = bp.extent(data, x='a', y='b')
    assert result == (1, 6, 7, 12), f'Expected (1, 6, 7, 12) but got {result}'


def test_extent_single_element() -> None:
    data = {'x': np.array([[1]]), 'y': np.array([[2]])}
    result = bp.extent(data)
    assert result == (1, 1, 2, 2), f'Expected (1, 1, 2, 2) but got {result}'


def test_extent_non_default_shape() -> None:
    data = {'x': np.array([1, 2, 3, 4, 5, 6]), 'y': np.array([7, 8, 9, 10, 11, 12])}
    result = bp.extent(data)
    assert result == (1, 6, 7, 12), f'Expected (1, 6, 7, 12) but got {result}'


def test_extent_unsorted_data() -> None:
    data = {
        'x': np.array([[3, 2, 1], [6, 5, 4]]),
        'y': np.array([[9, 8, 7], [12, 11, 10]]),
    }
    result = bp.extent(data)
    assert result == (3, 4, 9, 10), f'Expected (3, 4, 9, 10) but got {result}'


def test_fig_wspace_single_axes() -> None:
    fig, ax = plt.subplots()
    result = bp.fig_wspace(ax)
    sp = fig.subplotpars
    gs = ax.get_gridspec()
    assert isinstance(gs, matplotlib.gridspec.GridSpec)
    expected = (
        sp.wspace * (sp.right - sp.left) / (gs.ncols + sp.wspace * (gs.ncols - 1))
    )
    assert result == approx(expected), f'Expected {expected} but got {result}'
    plt.close(fig)


def test_fig_wspace_multiple_axes() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    for ax in axes.flatten():
        result = bp.fig_wspace(ax)
        sp = fig.subplotpars
        gs = ax.get_gridspec()
        expected = (
            sp.wspace * (sp.right - sp.left) / (gs.ncols + sp.wspace * (gs.ncols - 1))
        )
        assert result == approx(expected), f'Expected {expected} but got {result}'
    plt.close(fig)


def test_fig_wspace_custom_wspace() -> None:
    fig, ax = plt.subplots()
    fig.subplots_adjust(wspace=0.5)
    result = bp.fig_wspace(ax)
    sp = fig.subplotpars
    gs = ax.get_gridspec()
    assert isinstance(gs, matplotlib.gridspec.GridSpec)
    expected = (
        sp.wspace * (sp.right - sp.left) / (gs.ncols + sp.wspace * (gs.ncols - 1))
    )
    assert result == approx(expected), f'Expected {expected} but got {result}'
    plt.close(fig)


def test_fig_hspace_single_axes() -> None:
    fig, ax = plt.subplots()
    result = bp.fig_hspace(ax)
    sp = fig.subplotpars
    gs = ax.get_gridspec()
    assert isinstance(gs, matplotlib.gridspec.GridSpec)
    expected = (
        sp.hspace * (sp.top - sp.bottom) / (gs.nrows + sp.hspace * (gs.nrows - 1))
    )
    assert result == approx(expected), f'Expected {expected} but got {result}'
    plt.close(fig)


def test_fig_hspace_multiple_axes() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    for ax in axes.flatten():
        result = bp.fig_hspace(ax)
        sp = fig.subplotpars
        gs = ax.get_gridspec()
        expected = (
            sp.hspace * (sp.top - sp.bottom) / (gs.nrows + sp.hspace * (gs.nrows - 1))
        )
        assert result == approx(expected), f'Expected {expected} but got {result}'
    plt.close(fig)


def test_fig_hspace_custom_hspace() -> None:
    fig, ax = plt.subplots()
    fig.subplots_adjust(hspace=0.5)
    result = bp.fig_hspace(ax)
    sp = fig.subplotpars
    gs = ax.get_gridspec()
    assert isinstance(gs, matplotlib.gridspec.GridSpec)
    expected = (
        sp.hspace * (sp.top - sp.bottom) / (gs.nrows + sp.hspace * (gs.nrows - 1))
    )
    assert result == approx(expected), f'Expected {expected} but got {result}'
    plt.close(fig)


def test_subfig_label_default() -> None:
    fig, ax = plt.subplots()
    bp.subfig_label(ax, 0, 'center', 0.5, 0, 'center', 0.5, 0)
    text = ax.texts[0]
    assert text.get_text() == r'\textbf{(a)}'
    assert text.get_horizontalalignment() == 'center'
    assert text.get_verticalalignment() == 'center'
    assert text.get_position() == (0.5, 0.5)
    plt.close(fig)


def test_subfig_label_custom_index() -> None:
    fig, ax = plt.subplots()
    bp.subfig_label(ax, 2, 'center', 0.5, 0, 'center', 0.5, 0)
    text = ax.texts[0]
    assert text.get_text() == r'\textbf{(c)}'
    plt.close(fig)


def test_subfig_label_custom_position() -> None:
    fig, ax = plt.subplots()
    bp.subfig_label(ax, 0, 'left', 0.1, 0.05, 'bottom', 0.1, 0.05)
    text = ax.texts[0]
    assert text.get_text() == r'\textbf{(a)}'
    assert text.get_horizontalalignment() == 'left'
    assert text.get_verticalalignment() == 'bottom'
    assert text.get_position() == (0.1, 0.1)
    plt.close(fig)


def test_subfig_label_custom_kwargs() -> None:
    fig, ax = plt.subplots()
    bp.subfig_label(ax, 0, 'center', 0.5, 0, 'center', 0.5, 0, fontsize=12, color='red')
    text = ax.texts[0]
    assert text.get_text() == r'\textbf{(a)}'
    assert text.get_fontsize() == 12
    assert text.get_color() == 'red'
    plt.close(fig)


def test_subfig_label_non_integer_index() -> None:
    fig, ax = plt.subplots()
    bp.subfig_label(ax, '1', 'center', 0.5, 0, 'center', 0.5, 0)
    text = ax.texts[0]
    assert text.get_text() == r'\textbf{(1)}'
    plt.close(fig)


def test_auto_xlim_aspect_1_default_offset() -> None:
    fig, ax = plt.subplots()
    ax.set_ylim(0, 10)
    bp.auto_xlim_aspect_1(ax)
    y_min, y_max = ax.get_ylim()
    width, height = np.abs(ax.get_window_extent().size)
    dx = width / height * (y_max - y_min)
    expected_xlim = np.array([-0.5, +0.5]) * dx
    assert ax.get_xlim() == approx(
        expected_xlim
    ), f'Expected {expected_xlim} but got {ax.get_xlim()}'
    plt.close(fig)


def test_auto_xlim_aspect_1_with_offset() -> None:
    fig, ax = plt.subplots()
    ax.set_ylim(0, 10)
    offset = 2.0
    bp.auto_xlim_aspect_1(ax, offset=offset)
    y_min, y_max = ax.get_ylim()
    width, height = np.abs(ax.get_window_extent().size)
    dx = width / height * (y_max - y_min)
    expected_xlim = np.array([-0.5, +0.5]) * dx + offset
    assert ax.get_xlim() == approx(
        expected_xlim
    ), f'Expected {expected_xlim} but got {ax.get_xlim()}'
    plt.close(fig)


def test_auto_xlim_aspect_1_custom_ylim() -> None:
    fig, ax = plt.subplots()
    ax.set_ylim(-5, 5)
    bp.auto_xlim_aspect_1(ax)
    y_min, y_max = ax.get_ylim()
    width, height = np.abs(ax.get_window_extent().size)
    dx = width / height * (y_max - y_min)
    expected_xlim = np.array([-0.5, +0.5]) * dx
    assert ax.get_xlim() == approx(
        expected_xlim
    ), f'Expected {expected_xlim} but got {ax.get_xlim()}'
    plt.close(fig)


def test_auto_xlim_aspect_1_custom_size() -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_ylim(0, 10)
    bp.auto_xlim_aspect_1(ax)
    y_min, y_max = ax.get_ylim()
    width, height = np.abs(ax.get_window_extent().size)
    dx = width / height * (y_max - y_min)
    expected_xlim = np.array([-0.5, +0.5]) * dx
    assert ax.get_xlim() == approx(
        expected_xlim
    ), f'Expected {expected_xlim} but got {ax.get_xlim()}'
    plt.close(fig)


def test_common_lims_x_axis() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    for ax in axes.flatten():
        ax.set_xlim(np.random.rand(2) * 10)
    bp.common_lims('x', axes.flatten())
    xlims = [ax.get_xlim() for ax in axes.flatten()]
    assert all(
        xlim == xlims[0] for xlim in xlims
    ), f'Expected all xlims to be {xlims[0]} but got {xlims}'
    plt.close(fig)


def test_common_lims_y_axis() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    for ax in axes.flatten():
        ax.set_ylim(np.random.rand(2) * 10)
    bp.common_lims('y', axes.flatten())
    ylims = [ax.get_ylim() for ax in axes.flatten()]
    assert all(
        ylim == ylims[0] for ylim in ylims
    ), f'Expected all ylims to be {ylims[0]} but got {ylims}'
    plt.close(fig)


def test_common_lims_custom_vmin_vmax() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    for ax in axes.flatten():
        ax.set_xlim(np.random.rand(2) * 10)
    custom_vmin, custom_vmax = 0, 20
    bp.common_lims('x', axes.flatten(), vmin=custom_vmin, vmax=custom_vmax)
    xlims = [ax.get_xlim() for ax in axes.flatten()]
    assert all(
        xlim == (custom_vmin, custom_vmax) for xlim in xlims
    ), f'Expected all xlims to be {(custom_vmin, custom_vmax)} but got {xlims}'
    plt.close(fig)


def test_imshow_default_interp() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    extent = (0, 1, 0, 1)
    img = bp.imshow(ax, data, extent=extent)
    assert isinstance(img, matplotlib.image.AxesImage)
    assert (
        img.get_interpolation() == 'spline16'
    ), f"Expected 'spline16' but got {img.get_interpolation()}"
    assert img.get_extent() == [
        0,
        1,
        0,
        1,
    ], f'Expected {[0, 1, 0, 1]} but got {img.get_extent()}'
    assert (
        img.get_cmap().name == config.cmap.name
    ), f'Expected {config.cmap.name} but got {img.get_cmap().name}'
    plt.close(fig)


def test_imshow_no_interp() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    extent = (0, 1, 0, 1)
    img = bp.imshow(ax, data, extent, interp=False)
    assert isinstance(img, matplotlib.image.AxesImage)
    assert (
        img.get_interpolation() == 'auto'
    ), f"Matplotlib default interpolation is 'auto' but got {img.get_interpolation()}"
    plt.close(fig)


def test_imshow_custom_interp() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    extent = (0, 1, 0, 1)
    img = bp.imshow(ax, data, extent, interp='nearest')
    assert isinstance(img, matplotlib.image.AxesImage)
    assert (
        img.get_interpolation() == 'nearest'
    ), f"Expected 'nearest' but got {img.get_interpolation()}"
    plt.close(fig)


def test_imshow_custom_cmap() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    extent = (0, 1, 0, 1)
    custom_cmap = 'viridis'
    img = bp.imshow(ax, data, extent, cmap=custom_cmap)
    assert isinstance(img, matplotlib.image.AxesImage)
    assert (
        img.get_cmap().name == custom_cmap
    ), f'Expected {custom_cmap} but got {img.get_cmap().name}'
    plt.close(fig)


def test_imshow_additional_kwargs() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    extent = (0, 1, 0, 1)
    img = bp.imshow(ax, data, extent, alpha=0.5)
    assert isinstance(img, matplotlib.image.AxesImage)
    assert img.get_alpha() == 0.5, f'Expected 0.5 but got {img.get_alpha()}'
    plt.close(fig)


def test_markers_default() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y)
    line = ax.lines[0]
    assert np.array_equal(
        line.get_xdata(), x
    ), f'Expected x data {x} but got {line.get_xdata()!r}'
    assert np.array_equal(
        line.get_ydata(), y
    ), f'Expected y data {y} but got {line.get_ydata()!r}'
    assert line.get_marker() == 'o', f"Expected marker 'o' but got {line.get_marker()}"
    assert (
        line.get_markersize() == 8
    ), f'Expected marker size 8 but got {line.get_markersize()}'
    assert (
        line.get_markeredgecolor() == 'white'
    ), f"Expected marker edge color 'white' but got {line.get_markeredgecolor()}"
    assert (
        line.get_markeredgewidth() == 0.5
    ), f'Expected marker edge width 0.5 but got {line.get_markeredgewidth()}'
    assert (
        line.get_linestyle() == 'None'
    ), f"Expected line style 'None' but got {line.get_linestyle()}"
    plt.close(fig)


def test_markers_custom_marker() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y, marker='x')
    line = ax.lines[0]
    assert line.get_marker() == 'x', f"Expected marker 'x' but got {line.get_marker()}"
    plt.close(fig)


def test_markers_custom_size() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y, ms=10)
    line = ax.lines[0]
    assert (
        line.get_markersize() == 10
    ), f'Expected marker size 10 but got {line.get_markersize()}'
    plt.close(fig)


def test_markers_custom_edge_color() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y, mec='blue')
    line = ax.lines[0]
    assert (
        line.get_markeredgecolor() == 'blue'
    ), f"Expected marker edge color 'blue' but got {line.get_markeredgecolor()}"
    plt.close(fig)


def test_markers_custom_edge_width() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y, mew=1.0)
    line = ax.lines[0]
    assert (
        line.get_markeredgewidth() == 1.0
    ), f'Expected marker edge width 1.0 but got {line.get_markeredgewidth()}'
    plt.close(fig)


def test_markers_custom_line_style() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y, ls='-')
    line = ax.lines[0]
    assert (
        line.get_linestyle() == '-'
    ), f"Expected line style '-' but got {line.get_linestyle()}"
    plt.close(fig)


def test_markers_additional_kwargs() -> None:
    fig, ax = plt.subplots()
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    bp.markers(ax, x, y, color='green')
    line = ax.lines[0]
    assert (
        line.get_color() == 'green'
    ), f"Expected color 'green' but got {line.get_color()}"
    plt.close(fig)


def test_discretize_colormap_default_cmap() -> None:
    data = np.array([1, 2, 3, 4, 5])
    cmap, vmin, vmax, ticks = bp.discretize_colormap(data)
    assert (
        cmap.name == config.cmap.name
    ), f'Expected colormap {config.cmap.name} but got {cmap.name}'
    assert vmin == approx(0.5), f'Expected vmin 0.5 but got {vmin}'
    assert vmax == approx(5.5), f'Expected vmax 5.5 but got {vmax}'
    assert np.array_equal(
        ticks, np.arange(1, 6)
    ), f'Expected ticks [1, 2, 3, 4, 5] but got {ticks}'


def test_discretize_colormap_custom_cmap() -> None:
    data = np.array([1, 2, 3, 4, 5])
    custom_cmap = 'viridis'
    cmap, vmin, vmax, ticks = bp.discretize_colormap(data, colormap=custom_cmap)
    assert (
        cmap.name == custom_cmap
    ), f'Expected colormap {custom_cmap} but got {cmap.name}'
    assert vmin == approx(0.5), f'Expected vmin 0.5 but got {vmin}'
    assert vmax == approx(5.5), f'Expected vmax 5.5 but got {vmax}'
    assert np.array_equal(
        ticks, np.arange(1, 6)
    ), f'Expected ticks [1, 2, 3, 4, 5] but got {ticks}'


def test_discretize_colormap_single_value() -> None:
    data = np.array([3])
    cmap, vmin, vmax, ticks = bp.discretize_colormap(data)
    assert len(ticks) == 1, f'Expected colormap length 1 but got {cmap.N}'
    assert vmin == approx(2.5), f'Expected vmin 2.5 but got {vmin}'
    assert vmax == approx(3.5), f'Expected vmax 3.5 but got {vmax}'
    assert np.array_equal(ticks, np.array([3])), f'Expected ticks [3] but got {ticks}'


def test_discretize_colormap_negative_values() -> None:
    data = np.array([-3, -2, -1, 0, 1, 2, 3])
    cmap, vmin, vmax, ticks = bp.discretize_colormap(data)
    assert len(ticks) == 7, f'Expected colormap length 7 but got {cmap.N}'
    assert vmin == approx(-3.5), f'Expected vmin -3.5 but got {vmin}'
    assert vmax == approx(3.5), f'Expected vmax 3.5 but got {vmax}'
    assert np.array_equal(
        ticks, np.arange(-3, 4)
    ), f'Expected ticks [-3, -2, -1, 0, 1, 2, 3] but got {ticks}'


def test_cbar_beside_single_axes() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar, cax = bp.cbar_beside(fig, ax, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'vertical', 'cbar orientation is not vertical'
    plt.close(fig)


def test_cbar_beside_multiple_rows() -> None:
    fig, axes = plt.subplots(nrows=3)
    data = np.random.rand(10, 10)
    img = axes[0].imshow(data)
    cbar, cax = bp.cbar_beside(fig, axes, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'vertical', 'cbar orientation is not vertical'
    plt.close(fig)


def test_cbar_beside_multiple_columns() -> None:
    fig, axes = plt.subplots(ncols=3)
    data = np.random.rand(10, 10)
    img = axes[0].imshow(data)
    cbar, cax = bp.cbar_beside(fig, axes, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'vertical', 'cbar orientation is not vertical'
    plt.close(fig)


def test_cbar_beside_multiple_rows_and_columns() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    data = np.random.rand(10, 10)
    img = axes[0, 0].imshow(data)
    cbar, cax = bp.cbar_beside(fig, axes, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'vertical', 'cbar orientation is not vertical'
    plt.close(fig)


def test_cbar_beside_custom_dx() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    custom_dx = 0.05
    cbar, cax = bp.cbar_beside(fig, ax, img, dx=custom_dx)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'vertical', 'cbar orientation is not vertical'
    assert cax.get_position().xmin == approx(
        ax.get_position().xmax + custom_dx
    ), 'cax position is not correct'
    plt.close(fig)


def test_cbar_beside_additional_kwargs() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar, cax = bp.cbar_beside(fig, ax, img, label='Colorbar Label')
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'vertical', 'cbar orientation is not vertical'
    assert (
        cbar.ax.yaxis.get_label().get_text() == 'Colorbar Label'
    ), 'cbar label is not correct'
    plt.close(fig)


def test_cbar_above_single_axes() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar, cax = bp.cbar_above(fig, ax, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'horizontal', 'cbar orientation is not horizontal'
    assert cax.xaxis.get_ticks_position() == 'top', 'cax ticks position is not top'
    assert cax.xaxis.get_label_position() == 'top', 'cax label position is not top'
    plt.close(fig)


def test_cbar_above_multiple_rows() -> None:
    fig, axes = plt.subplots(nrows=3)
    data = np.random.rand(10, 10)
    img = axes[0].imshow(data)
    cbar, cax = bp.cbar_above(fig, axes, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'horizontal', 'cbar orientation is not horizontal'
    assert cax.xaxis.get_ticks_position() == 'top', 'cax ticks position is not top'
    assert cax.xaxis.get_label_position() == 'top', 'cax label position is not top'
    plt.close(fig)


def test_cbar_above_multiple_columns() -> None:
    fig, axes = plt.subplots(ncols=3)
    data = np.random.rand(10, 10)
    img = axes[0].imshow(data)
    cbar, cax = bp.cbar_above(fig, axes, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'horizontal', 'cbar orientation is not horizontal'
    assert cax.xaxis.get_ticks_position() == 'top', 'cax ticks position is not top'
    assert cax.xaxis.get_label_position() == 'top', 'cax label position is not top'
    plt.close(fig)


def test_cbar_above_multiple_rows_and_columns() -> None:
    fig, axes = plt.subplots(nrows=2, ncols=2)
    data = np.random.rand(10, 10)
    img = axes[0, 0].imshow(data)
    cbar, cax = bp.cbar_above(fig, axes, img)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'horizontal', 'cbar orientation is not horizontal'
    assert cax.xaxis.get_ticks_position() == 'top', 'cax ticks position is not top'
    assert cax.xaxis.get_label_position() == 'top', 'cax label position is not top'
    plt.close(fig)


def test_cbar_above_custom_dy() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    custom_dy = 0.05
    cbar, cax = bp.cbar_above(fig, ax, img, dy=custom_dy)
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'horizontal', 'cbar orientation is not horizontal'
    assert cax.get_position().ymin == approx(
        ax.get_position().ymax + custom_dy
    ), 'cax position is not correct'
    plt.close(fig)


def test_cbar_above_additional_kwargs() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar, cax = bp.cbar_above(fig, ax, img, label='Colorbar Label')
    assert isinstance(
        cbar, matplotlib.colorbar.Colorbar
    ), 'cbar is not a matplotlib Colorbar'
    assert isinstance(cax, plt.Axes), 'cax is not a matplotlib Axes'
    assert cbar.orientation == 'horizontal', 'cbar orientation is not horizontal'
    assert (
        cbar.ax.xaxis.get_label().get_text() == 'Colorbar Label'
    ), 'cbar label is not correct'
    plt.close(fig)


def test_cbar_minmax_labels_default_labels() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar = fig.colorbar(img, orientation='horizontal')
    bp.cbar_minmax_labels(cbar)
    expected_labels = [bp.fmt_num(np.min(data)), bp.fmt_num(np.max(data))]
    assert cbar.get_ticks() == approx(
        cbar.mappable.get_clim()
    ), f'Expected ticks {cbar.mappable.get_clim()} but got {cbar.get_ticks()}'
    assert [
        label.get_text() for label in cbar.ax.get_xticklabels()
    ] == expected_labels, (
        f'Expected labels {expected_labels} but got '
        f'{[label.get_text() for label in cbar.ax.get_xticklabels()]}'
    )
    plt.close(fig)


def test_cbar_minmax_labels_vmin_vmax() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    vmin, vmax = 0.2, 0.8
    img = ax.imshow(data, vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(img, orientation='horizontal')
    bp.cbar_minmax_labels(cbar)
    expected_labels = [bp.fmt_num(vmin), bp.fmt_num(vmax)]
    assert cbar.get_ticks() == approx(
        cbar.mappable.get_clim()
    ), f'Expected ticks {cbar.mappable.get_clim()} but got {cbar.get_ticks()}'
    assert [
        label.get_text() for label in cbar.ax.get_xticklabels()
    ] == expected_labels, (
        f'Expected labels {expected_labels} but got '
        f'{[label.get_text() for label in cbar.ax.get_xticklabels()]}'
    )
    plt.close(fig)


def test_cbar_minmax_labels_custom_labels() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar = fig.colorbar(img, orientation='horizontal')
    custom_labels = ['Low', 'High']
    bp.cbar_minmax_labels(cbar, labels=custom_labels)
    assert cbar.get_ticks() == approx(
        cbar.mappable.get_clim()
    ), f'Expected ticks {cbar.mappable.get_clim()} but got {cbar.get_ticks()}'
    assert [label.get_text() for label in cbar.ax.get_xticklabels()] == custom_labels, (
        f'Expected labels {custom_labels} but got '
        f'{[label.get_text() for label in cbar.ax.get_xticklabels()]}'
    )
    plt.close(fig)


def test_cbar_minmax_labels_custom_format() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar = fig.colorbar(img, orientation='horizontal')
    bp.cbar_minmax_labels(cbar, fmt='.2f')
    expected_labels = [bp.fmt_num(x, fmt='.2f') for x in cbar.mappable.get_clim()]
    assert cbar.get_ticks() == approx(
        cbar.mappable.get_clim()
    ), f'Expected ticks {cbar.mappable.get_clim()} but got {cbar.get_ticks()}'
    assert [
        label.get_text() for label in cbar.ax.get_xticklabels()
    ] == expected_labels, (
        f'Expected labels {expected_labels} but got '
        f'{[label.get_text() for label in cbar.ax.get_xticklabels()]}'
    )
    plt.close(fig)


def test_cbar_minmax_labels_horizontal_alignment() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar = fig.colorbar(img, orientation='horizontal')
    bp.cbar_minmax_labels(cbar)
    expected_labels = [bp.fmt_num(x) for x in cbar.mappable.get_clim()]
    assert cbar.get_ticks() == approx(
        cbar.mappable.get_clim()
    ), f'Expected ticks {cbar.mappable.get_clim()} but got {cbar.get_ticks()}'
    assert [
        label.get_text() for label in cbar.ax.get_xticklabels()
    ] == expected_labels, (
        f'Expected labels {expected_labels} but got '
        f'{[label.get_text() for label in cbar.ax.get_xticklabels()]}'
    )
    for align, label in zip(
        ('left', 'right'), cbar.ax.xaxis.get_ticklabels(), strict=True
    ):
        assert (
            label.get_horizontalalignment() == align
        ), f'Expected horizontal alignment {align} but got {label.get_horizontalalignment()}'
    plt.close(fig)


def test_cbar_minmax_labels_vertical_alignment() -> None:
    fig, ax = plt.subplots()
    data = np.random.rand(10, 10)
    img = ax.imshow(data)
    cbar = fig.colorbar(img, orientation='vertical')
    bp.cbar_minmax_labels(cbar)
    expected_labels = [bp.fmt_num(x) for x in cbar.mappable.get_clim()]
    assert cbar.get_ticks() == approx(
        cbar.mappable.get_clim()
    ), f'Expected ticks {cbar.mappable.get_clim()} but got {cbar.get_ticks()}'
    assert [
        label.get_text() for label in cbar.ax.get_yticklabels()
    ] == expected_labels, (
        f'Expected labels {expected_labels} but got '
        f'{[label.get_text() for label in cbar.ax.get_yticklabels()]}'
    )
    for align, label in zip(
        ('bottom', 'top'), cbar.ax.yaxis.get_ticklabels(), strict=True
    ):
        assert (
            label.get_verticalalignment() == align
        ), f'Expected vertical alignment {align} but got {label.get_verticalalignment()}'
    plt.close(fig)


def test_legend_default_options() -> None:
    fig, ax = plt.subplots()
    (line,) = ax.plot([0, 1], [0, 1], label='Test Line')
    legend = bp.legend(ax)
    assert isinstance(
        legend, matplotlib.legend.Legend
    ), 'legend is not a matplotlib Legend'
    assert legend.get_frame_on(), 'legend frame is off'
    assert legend.handlelength == 1.5, 'legend handle length is not 1.5'
    assert legend.borderaxespad == 0.2, 'legend border axes pad is not 0.2'
    assert legend.columnspacing == 1.5, 'legend column spacing is not 1.5'
    assert legend.handletextpad == 0.5, 'legend handle text pad is not 0.5'
    plt.close(fig)


def test_legend_custom_options() -> None:
    fig, ax = plt.subplots()
    (line,) = ax.plot([0, 1], [0, 1], label='Test Line')
    legend = bp.legend(ax, loc='upper left', fontsize=12, frameon=True)
    assert isinstance(
        legend, matplotlib.legend.Legend
    ), 'legend is not a matplotlib Legend'
    assert legend.get_frame_on(), 'legend frame is off'
    assert legend.get_texts()[0].get_fontsize() == 12, 'legend font size is not 12'
    assert legend._loc == 2, 'legend location is not upper left'  # type: ignore[attr-defined]
    plt.close(fig)


def test_legend_additional_kwargs() -> None:
    fig, ax = plt.subplots()
    (line,) = ax.plot([0, 1], [0, 1], label='Test Line')
    legend = bp.legend(ax, title='Legend Title', shadow=True)
    assert isinstance(
        legend, matplotlib.legend.Legend
    ), 'legend is not a matplotlib Legend'
    assert (
        legend.get_title().get_text() == 'Legend Title'
    ), 'legend title is not correct'
    assert legend.shadow, 'legend shadow is not enabled'
    plt.close(fig)


def test_text_default() -> None:
    fig, ax = plt.subplots()
    bp.text(ax, 'center', 0.5, 0, 'center', 0.5, 0, 'Test Text')
    text = ax.texts[0]
    assert text.get_text() == 'Test Text'
    assert text.get_horizontalalignment() == 'center'
    assert text.get_verticalalignment() == 'center'
    assert text.get_position() == (0.5, 0.5)
    plt.close(fig)


def test_text_custom_position() -> None:
    fig, ax = plt.subplots()
    bp.text(ax, 'left', 0.1, 0.05, 'bottom', 0.1, 0.05, 'Test Text')
    text = ax.texts[0]
    _bp = config.bp
    assert text.get_text() == 'Test Text'
    assert text.get_horizontalalignment() == 'left'
    assert text.get_verticalalignment() == 'bottom'
    assert text.get_position() == (0.1, 0.1)
    assert ax.figure is not None
    assert text.get_transform() == ax.transAxes + mtrans.ScaledTranslation(
        0.05 * _bp, 0.05 * _bp, ax.figure.dpi_scale_trans
    )
    plt.close(fig)


def test_text_custom_kwargs() -> None:
    fig, ax = plt.subplots()
    bp.text(
        ax, 'center', 0.5, 0, 'center', 0.5, 0, 'Test Text', fontsize=12, color='red'
    )
    text = ax.texts[0]
    assert text.get_text() == 'Test Text'
    assert text.get_fontsize() == 12
    assert text.get_color() == 'red'
    plt.close(fig)


def test_text_with_offset() -> None:
    fig, ax = plt.subplots()
    bp.text(ax, 'center', 0.5, 0.1, 'center', 0.5, 0.1, 'Test Text')
    text = ax.texts[0]
    _bp = config.bp
    assert text.get_text() == 'Test Text'
    assert text.get_horizontalalignment() == 'center'
    assert text.get_verticalalignment() == 'center'
    assert text.get_position() == (0.5, 0.5)
    assert ax.figure is not None
    assert text.get_transform() == ax.transAxes + mtrans.ScaledTranslation(
        0.1 * _bp, 0.1 * _bp, ax.figure.dpi_scale_trans
    )
    plt.close(fig)


def test_add_arrow_to_axes() -> None:
    fig, ax = plt.subplots()
    from_pos = (0.1, 0.1)
    to_pos = (0.9, 0.9)
    bp.add_arrow(ax, from_pos, to_pos)
    arrow = ax.patches[0]
    assert isinstance(arrow, mpatches.FancyArrowPatch), 'arrow is not a FancyArrowPatch'
    arrowstyle = arrow.get_arrowstyle()
    assert isinstance(arrow, mpatches.FancyArrowPatch), 'arrow is not a FancyArrowPatch'
    assert arrow.get_edgecolor() == (
        0.0,
        0.0,
        0.0,
        1,
    ), f'Expected color (0.0, 0.0, 0.0, 1) but got {arrow.get_edgecolor()}'
    assert (
        arrow.get_linewidth() == 1.5
    ), f'Expected linewidth 1.5 but got {arrow.get_linewidth()}'
    assert isinstance(
        arrowstyle, mpatches.ArrowStyle.Fancy
    ), 'arrowstyle is not a Fancy ArrowStyle'
    plt.close(fig)


def test_add_arrow_to_figure() -> None:
    fig, ax = plt.subplots()
    from_pos = (0.1, 0.1)
    to_pos = (0.9, 0.9)
    bp.add_arrow(fig, from_pos, to_pos)
    arrow = fig.artists[0]
    assert isinstance(arrow, mpatches.FancyArrowPatch), 'arrow is not a FancyArrowPatch'
    arrowstyle = arrow.get_arrowstyle()
    assert isinstance(arrow, mpatches.FancyArrowPatch), 'arrow is not a FancyArrowPatch'
    assert arrow.get_edgecolor() == (
        0.0,
        0.0,
        0.0,
        1,
    ), f'Expected color (0.0, 0.0, 0.0, 1) but got {arrow.get_edgecolor()}'
    assert (
        arrow.get_linewidth() == 1.5
    ), f'Expected linewidth 1.5 but got {arrow.get_linewidth()}'
    assert isinstance(
        arrowstyle, mpatches.ArrowStyle.Fancy
    ), 'arrowstyle is not a Fancy ArrowStyle'
    plt.close(fig)


def test_add_arrow_custom_color() -> None:
    fig, ax = plt.subplots()
    from_pos = (0.1, 0.1)
    to_pos = (0.9, 0.9)
    custom_color = 'red'
    custom_color_rgba = to_rgba(custom_color)
    bp.add_arrow(ax, from_pos, to_pos, color=custom_color)
    arrow = ax.patches[0]
    assert (
        arrow.get_edgecolor() == custom_color_rgba
    ), f'Expected color {custom_color_rgba} but got {arrow.get_edgecolor()}'
    plt.close(fig)


def test_add_arrow_custom_linewidth() -> None:
    fig, ax = plt.subplots()
    from_pos = (0.1, 0.1)
    to_pos = (0.9, 0.9)
    custom_lw = 2.0
    bp.add_arrow(ax, from_pos, to_pos, lw=custom_lw)
    arrow = ax.patches[0]
    assert (
        arrow.get_linewidth() == custom_lw
    ), f'Expected linewidth {custom_lw} but got {arrow.get_linewidth()}'
    plt.close(fig)


def test_add_arrow_custom_arrowstyle() -> None:
    fig, ax = plt.subplots()
    from_pos = (0.1, 0.1)
    to_pos = (0.9, 0.9)
    custom_arrowstyle = '->'
    bp.add_arrow(ax, from_pos, to_pos, arrowstyle=custom_arrowstyle)
    arrow = ax.patches[0]
    assert isinstance(arrow, mpatches.FancyArrowPatch), 'arrow is not a FancyArrowPatch'
    arrowstyle = arrow.get_arrowstyle()
    assert isinstance(
        arrowstyle, mpatches.ArrowStyle.CurveB
    ), 'arrowstyle is not a CurveB ArrowStyle'
    plt.close(fig)


def test_add_arrow_custom_properties() -> None:
    fig, ax = plt.subplots()
    from_pos = (0.1, 0.1)
    to_pos = (0.9, 0.9)
    custom_properties = 'fancy, head_length=8, head_width=8, tail_width=2'
    bp.add_arrow(ax, from_pos, to_pos, arrowstyle=custom_properties)
    arrow = ax.patches[0]
    assert isinstance(arrow, mpatches.FancyArrowPatch), 'arrow is not a FancyArrowPatch'
    plt.close(fig)


def test_minimal_example() -> None:
    t = np.linspace(0, 10, 1000)
    y = 5 * np.exp(-t / 2) * np.cos(2 * np.pi * t)
    root = Path(__file__).parent.parent
    config.output_path = root / 'docs/example_plots'
    fig, ax = bp.newfig(left=40, bottom=35)
    ax.plot(t, y, label='Damped Oscillation')
    ax.set_xlabel('Time $t$ / s')
    ax.set_ylabel('Amplitude $A(t)$ / cm')
    bp.legend(ax)
    bp.save_figure(fig, 'damped_oscillation.png')
