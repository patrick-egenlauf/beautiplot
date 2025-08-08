# # Configuration
#
# This file contains an example of how to configure the beautiplot
# library according to your needs. The configuration allows you to set
# various parameters such as output paths, font sizes, and other
# settings that will be applied to all plots created with beautiplot.
# All configuration options are documented with examples in the
# [`config`][beautiplot._config._Config] class. Here, we will
# summarize the most important options and how to use them.
#
# ## Global Configuration
#
# We start by importing the necessary instance.

import beautiplot.plot as bp
from beautiplot import config

# The `config` object is an instance of the `_Config` class, which
# allows you to set global configuration options.
#
# !!! warning
#
#     You should never import and instantiate the `_Config` class
#     directly, but always use the `config` object provided by the
#     `beautiplot` module.
#
# The [`output_path`][beautiplot._config._Config.output_path] option
# specifies the directory where the plots will be saved. You can set it
# to any valid path on your system. We will save the plots in a
# directory called `example_plots` in the current working directory.
# If the directory does not exist, it will be created automatically.

config.output_path = 'docs/example_plots'

# You should definitely set the width of the plots to the width of
# your document. This ensures that the text inside the plots has the
# same size as the text in your document. The width is specified in
# points (pt) and you can get the width of your document in LaTeX by
# including
#
# ``` { .latex .copy }
# \the\textwidth
# ```
#
# in your document and compiling it. We will assume that the width of
# our document is 400pt and set the
# [`width`][beautiplot._config._Config.width] option accordingly.

config.width = 400

# The default color map used by beautiplot is `inferno`. You can change
# it to any other color map supported by Matplotlib or a custom one by
# using the [`set_cmap`][beautiplot._config._Config.set_cmap]` method.
# We will set the color map to `viridis`.

config.set_cmap('viridis')

# ## Plot Specific Configuration
#
# You can also set plot-specific configuration options. Most of the
# functions in the [`plot`][beautiplot.plot] module have arguments that,
# if specified, will override the global configuration or take
# additional keyword arguments that can be used to customize the plot
# and override the global configuration.
#
# Some examples of plot-specific configuration options are using a
# different color map, figure width or aspect ratio.

fig, axes = bp.newfig(width=0.5, aspect=1.5)
bp.imshow(axes, [[1, 2], [3, 4]], extent=(0, 1, 0, 1), cmap='plasma')

# The `width` argument sets the width of the figure to 50% of the
# global configuration width, and the `aspect` argument sets the aspect
# ratio of the figure to 1.5. The `cmap` argument overrides the global
# color map setting and uses `plasma` for this specific plot.
