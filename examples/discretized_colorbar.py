# # Discretized Colorbar
#
# This example demonstrates how to create a discretized colormap for
# categorical data, such as regions or clusters in a 2D grid. The
# colormap is created based on the maximum and minimum values of the
# data, and the colorbar is displayed above the plot.
#
# We start by importing the necessary libraries and defining the
# configuration for the plot.

from pathlib import Path

import numpy as np

import beautiplot.plot as bp
from beautiplot import config

root = Path(__file__).parent.parent
config.output_path = root / 'docs/example_plots'

# Next, we define the data for the plot. In this example, we create a
# grid of points and assign each point to a region based on its
# proximity to predefined attractors. The regions are represented by
# integers, which will be used to create a discretized colormap.

x = np.linspace(-2.1, 2.1, 1000)
y = np.linspace(-2.1, 2.1, 1000)
X, Y = np.meshgrid(x, y)
attractors = np.array([[1, 1], [-1, -1], [1, -1]])
marker_x, marker_y = attractors[:, 0], attractors[:, 1]
distances = np.stack([np.sqrt((X - px) ** 2 + (Y - py) ** 2) for px, py in attractors])
regions = np.argmin(distances, axis=0)

# To visualize the regions, we use the
# [`discretize_colormap`][beautiplot.plot.discretize_colormap] function.
# This function is designed for arrays of integers, such as region or
# category indices. It automatically creates a colormap with a distinct
# color for each integer value in the data. The number of colors is
# determined by the difference between the minimum and maximum values in
# the array. The colorbar ticks are placed in the center of each color
# segment, and the tick labels correspond to the integer values present
# in the data.

cmap, vmin, vmax, ticks = bp.discretize_colormap(regions, 'plasma')

# We also define the extent of the data for the imshow plot using the
# [`extent`][beautiplot.plot.extent] function.

data_dict = {'x': x, 'y': y}
ext = bp.extent(data_dict)

# Then, we create a new figure and axis using the
# [`newfig`][beautiplot.plot.newfig] function. At first, we need to
# estimate the margins, but we can adjust them later if needed.
#
# `beautiplot` will suggest margin adjustments when saving the figure.
# Keep in mind that these adjustments might affect tick labels, so
# fixing tick locations can help avoid a cycle of suggestions.
#
# We plot the regions using the [`imshow`][beautiplot.plot.imshow]
# function, which displays the regions with the discretized colormap.

fig, ax = bp.newfig(left=45, bottom=32, top=46)
im = bp.imshow(ax, regions, extent=ext, cmap=cmap, vmin=vmin, vmax=vmax)

# We also add markers for the attractors using the
# [`markers`][beautiplot.plot.markers] function.

bp.markers(ax, marker_x, marker_y, label='Attractors')

# We set the x and y labels.

ax.set_xlabel('x')
ax.set_ylabel('y')

# Here, we create a colorbar above the plot using the
# [`cbar_above`][beautiplot.plot.cbar_above] function. The colorbar is
# labeled with "Region Index", and the ticks are set to the unique
# values of the regions.

cbar, cax = bp.cbar_above(fig, ax, im, ticks=ticks)
cbar.set_label('Region Index')

# Finally, we add a legend to the plot using the
# [`legend`][beautiplot.plot.legend] function, and we save the figure
# using the
# [`save_figure`][beautiplot.plot.save_figure] function.

bp.legend(ax)
bp.save_figure(fig, 'voronoi_attractors.png')

# ![voronoi_attractors.png](../example_plots/voronoi_attractors.png)
