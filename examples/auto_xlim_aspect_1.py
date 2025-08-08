# # Adjust x-limits to maintain aspect ratio 1
#
# This example demonstrates how to adjust the x-limits of a plot to
# maintain an aspect ratio of 1. This is useful whenever you want that
# one unit on the x-axis is the same length as one unit on the y-axis.
# This is important for example in the following cases:
#
# - Visualizing geometric shapes: Circles, squares, or any object where
#   equal scaling is needed (e.g., plotting a circle should look round,
#   not elliptical).
# - Physical simulations: When plotting spatial domains (e.g.,
#   diffusion, wave, or field simulations) where distances in x and y
#   should be directly comparable.
#
# We start by importing the necessary libraries and setting up the
# configuration for the plots.

from pathlib import Path

import numpy as np

import beautiplot.plot as bp
from beautiplot import config

root = Path(__file__).parent.parent
config.output_path = root / 'docs/example_plots'

# We define the data for the plot. In this case, we create a sine wave
# but switch the x and y axes to demonstrate the aspect ratio
# adjustment.

y = np.linspace(-2, 2, 100)
x = np.sin(y)

# We then create a new figure with the specified margins. In the
# beginning, you need to guess the margins and spacing, but you can
# adjust them later if needed.

fig, ax = bp.newfig(left=34, bottom=20, top=5)

# Next, we plot the data. We set the y-limits to ensure that the plot
# has a range of -2 to 2, which is important for the aspect ratio
# adjustment.

ax.plot(x, y)
ax.set_ylim(-2, 2)

# We save the figure with the standard x-limits to show the initial
# state of the plot.

bp.save_figure(fig, 'standard_xlim.png')

# ![standard_xlim.png](../example_plots/standard_xlim.png)
#
# Now, we can adjust the x-limits to maintain an aspect ratio of 1 with
# the [`auto_xlim_aspect_1`][beautiplot.plot.auto_xlim_aspect_1]
# function.

bp.auto_xlim_aspect_1(ax)
bp.save_figure(fig, 'auto_xlim_aspect_1.png')

# ![auto_xlim_aspect_1.png](../example_plots/auto_xlim_aspect_1.png)
