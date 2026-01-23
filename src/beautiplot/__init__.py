"""This module provides functionalities for creating beautiful plots.

## Modules

- [`config`](_config/config.md): Contains configuration
    settings for beautiplot.
- [`plot`][beautiplot.plot]: Contains functions for creating beautiful
    plots.
"""

from importlib.metadata import version

from . import plot
from ._config import config

__all__ = ['config', 'plot']
__version__ = version('beautiplot')
