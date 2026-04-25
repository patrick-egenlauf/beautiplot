# Copyright 2020 Johannes Reiff modified by Patrick Egenlauf
# SPDX-License-Identifier: MIT
"""Plotting utilities."""

import matplotlib

# Configure matplotlib backend to pgf
matplotlib.use('pgf')

from .colorbar import (
    cbar_above,
    cbar_beside,
    cbar_minmax_labels,
    discretize_colormap,
)
from .elements import (
    add_arrow,
    imshow,
    legend,
    markers,
    subfig_label,
    text,
)
from .figure import newfig, save_figure
from .layout import (
    auto_xlim_aspect_1,
    common_lims,
    extent,
    fig_hspace,
    fig_wspace,
)
from .utils import fmt_num, log

__all__ = [
    'add_arrow',
    'auto_xlim_aspect_1',
    'cbar_above',
    'cbar_beside',
    'cbar_minmax_labels',
    'common_lims',
    'discretize_colormap',
    'extent',
    'fig_hspace',
    'fig_wspace',
    'fmt_num',
    'imshow',
    'legend',
    'log',
    'markers',
    'newfig',
    'save_figure',
    'subfig_label',
    'text',
]
