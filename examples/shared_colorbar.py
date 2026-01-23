# # Shared Colorbar
#
# This example demonstrates how to create a grid of subplots with a
# shared colorbar using the `beautiplot` library. The subplots display
# the probability densities of a 2D quantum harmonic oscillator.
#
# We start by importing necessary libraries and setting up the
# configuration for the plots.

from pathlib import Path

import numpy as np
from scipy.special import factorial, hermite

import beautiplot.plot as bp
from beautiplot import config

root = Path(__file__).parent.parent
config.output_path = root / 'docs/example_plots'
config.fontsize = 11

# Next, we define the parameters for the 2D grid of subplots and the
# quantum states we want to visualize.

nx, ny = 100, 100
x = np.linspace(-4, 4, nx)
y = np.linspace(-4, 4, ny)
X, Y = np.meshgrid(x, y)
states = [(0, 0), (1, 0), (0, 1), (1, 1)]

# To ensuure that all subplots have the same extent, we calculate the
# extent of the data using the
# [`extent`][beautiplot.plot.extent] function.

data_dict = {'x': x, 'y': y}
ext = bp.extent(data_dict)

# The `psi_2d` function computes the normalized wavefunction of the 2D
# quantum harmonic oscillator for given quantum numbers `nx` and `ny`.
# It uses the Hermite polynomials and the Gaussian function.


def psi_2d(nx, ny, X, Y):
    Hx = hermite(nx)(X)
    Hy = hermite(ny)(Y)
    norm = 1.0 / np.sqrt(np.pi * 2 ** (nx + ny) * factorial(nx) * factorial(ny))
    return norm * Hx * Hy * np.exp(-0.5 * (X**2 + Y**2))


# To start plotting, we create a new figure with a grid of subplots. In
# the beginning, you need to guess the margins and spacing, but you can
# adjust them later if needed.
#
# When saving, `beautiplot` will suggest adjustments for margins and
# spacing (wspace/hspace) if overlaps or cut-offs are detected. Be aware
# that these adjustments can influence tick generation, so fixing ticks
# might be necessary for a stable layout.

fig, axes = bp.newfig(
    nrows=2, ncols=2, left=39, bottom=33, top=38, right=62, wspace=26, hspace=26
)

# We want to label each subplot with a subfigure label. The `label
# positions` list defines the positions of the labels in each subplot.

label_positions = [
    ('right', 0.0, -22, 'bottom', 1.0, 3),
    ('right', 0.0, 0, 'bottom', 1.0, 3),
    ('right', 0.0, -22, 'bottom', 1.0, 3),
    ('right', 0.0, 0, 'bottom', 1.0, 3),
]

# We then iterate over the quantum states, compute the wavefunction, and
# plot the probability density in each subplot. The
# [`imshow`][beautiplot.plot.imshow] function is used to display the
# data as an image. The bounding box in data coordinates that the image
# will fill is controlled by the `extent` parameter. Thus, we can use
# the `extent` calculated earlier to ensure all subplots have the same
# extent. The [`subfig_label`][beautiplot.plot.subfig_label] function
# adds the subfigure label to each subplot. The titles of the subplots
# are set to indicate the quantum numbers. You can use LaTeX formatting
# for the titles and labels. We store the images in a list to later set
# the same color limits for all subplots.

ims = []
for i, (n_x, n_y) in enumerate(states):
    psi = psi_2d(n_x, n_y, X, Y)
    prob_density = np.abs(psi) ** 2
    ax = axes.flat[i]
    im = bp.imshow(ax, prob_density, extent=ext)
    bp.subfig_label(ax, i, *label_positions[i])
    ax.set_title(f'$n_x={n_x}, n_y={n_y}$', fontsize=11)
    ims.append(im)

# After plotting, we set the x and y labels for the subplots. To reduce
# clutter, we can remove the x-tick labels for the top subplots and the
# y-tick labels for the right subplots.

for i in range(2):
    axes[0, i].set_xticklabels([])
    axes[i, 1].set_yticklabels([])
    axes[i, 0].set_ylabel('$y$ / a.u.')
    axes[1, i].set_xlabel('$x$ / a.u.')

# We calculate the maximum value of the probability densities across all
# subplots to set a common color limit for the colorbar. This ensures
# that the color mapping is consistent across all subplots. If you
# already have the data before plotting (in our case, `prob_density`
# before the loop), you can directly use the maximum and minimum values
# of the data to set the color limitsin the
# [`imshow`][beautiplot.plot.imshow] function via the `vmin` and `vmax`
# parameters.

vmax = max(im.get_array().max() for im in ims)
for im in ims:
    im.set_clim(0, vmax)

# Finally, we create a colorbar beside the grid of subplots using the
# [`cbar_beside`][beautiplot.plot.cbar_beside] function. By storing
# the returned colorbar and axis in two variables, we can set a label
# for the colorbar.

cbar, cax = bp.cbar_beside(fig, axes, ims[0], dx=0.02)
cbar.set_label(r'Probability Density $|\psi(x, y)|^2$')

# We add a title to the figure and store it in a file. Here, we use
# `png` for visualization reasons, but you should use `pdf` or `svg`
# for publication-quality figures. In case of really large figures,
# memory wise, you can still use `png` to save memory.
# The [`save_figure`][beautiplot.plot.save_figure] function saves
# the figure in the directory specified in the `config.output_path`.
# The filename is specified as the second argument.

fig.suptitle('2D Quantum Harmonic Oscillator Probability Densities')
bp.save_figure(fig, '2d_quantum_harmonic_oscillator.png')

# ![2d_quantum_harmonic_oscillator.png](../example_plots/2d_quantum_harmonic_oscillator.png)
