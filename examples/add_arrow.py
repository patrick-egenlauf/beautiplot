# # Adding an Arrow and Text to a Plot
#
# This example demonstrates how to add an arrow and text to a plot using
# the `beautiplot` library.
#
# We start by importing the necessary libraries and defining the
# configuration for the plot.

from pathlib import Path

import numpy as np

import beautiplot.plot as bp
from beautiplot import config

root = Path(__file__).parent.parent
config.output_path = root / 'docs/example_plots'

# Next, we generate some data for the plot. In this example, we create a
# 2D grid of points and compute a simple function over that grid. The
# data will be used to create an image plot.

x = np.linspace(0, 1, 100)
y = np.linspace(0, 1, 100)
X, Y = np.meshgrid(x, y)
Z = X + Y

# The extent can be calculated using the
# [`extent`][beautiplot.plot.extent] function, which takes a dictionary
# with keys 'x' and 'y' representing the x and y coordinates of the
# data.

data_dict = {'x': x, 'y': y}
ext = bp.extent(data_dict)

# We then create a new figure and axes using the
# [`newfig`][beautiplot.plot.newfig] function. At first, you need to
# estimate the margins, but you can adjust them later if needed. The
# figure will be trimmed to the axes, and tick labels or axis labels
# won't be visible unless you specify margins.
# We use the [`imshow`][beautiplot.plot.imshow] function to create an
# image plot of the data. The `extent` parameter is used to set the
# limits of the x and y axes, and the `cmap` parameter specifies the
# colormap to use for the image. We also set the y-ticks to specific
# values to demonstrate how to customize the tick labels.

fig, ax = bp.newfig(left=36, bottom=30, right=43)
im = bp.imshow(ax, Z, extent=ext, cmap='viridis')
ax.set_yticks([0.1, 0.3, 0.5, 0.7, 0.9])

# Now, we can add an arrow to the plot using the
# [`add_arrow`][beautiplot.plot.add_arrow] function. This function
# allows you to specify the starting and ending points of the arrow in
# normalized coordinates (0 to 1) relative to the axes. The arrow will
# be drawn from the starting point to the ending point.
# In this example, we add an arrow from the bottom left to the top right
# of the axes.

bp.add_arrow(ax, (0.1, 0.1), (0.9, 0.9))

# We can also add text to the plot using the
# [`text`][beautiplot.plot.text] function. This function allows you to
# specify the position of the text in normalized coordinates, as well as
# the text itself. In this example, we add text at the top right corner
# of the axes, indicating that the arrow points to increasing values of
# `x + y`.

bp.text(ax, ha='right', x=0.92, dx=0, va='bottom', y=0.92, dy=0, txt='Increasing $x+y$')

# To add a colorbar to the plot, we use the
# [`cbar_beside`][beautiplot.plot.cbar_beside] function. This function
# creates a colorbar beside the image plot, and we can also set the
# minimum and maximum labels for the colorbar using the
# [`cbar_minmax_labels`][beautiplot.plot.cbar_minmax_labels] function.
# The colorbar will display the range of values in the image plot, and
# the labels will indicate the minimum and maximum values of `x + y`.
# In addition, we set labels for the x, y axes, and the colorbar.

cbar, cax = bp.cbar_beside(fig, ax, im)
bp.cbar_minmax_labels(cbar)
cbar.set_label('$x + y$')
ax.set_xlabel('Horizontal Position $x$')
ax.set_ylabel('Vertical Position $y$')

# Finally, we save the figure using the
# [`save_figure`][beautiplot.plot.save_figure] function. This function
# saves the figure to the specified output path with a given filename.
# Here, we us `png` for visualization purposes, but you should use
# `pdf` for publication-quality figures.

bp.save_figure(fig, 'arrow_text_example.png')

# ![arrow_text_example.png](../example_plots/arrow_text_example.png)
