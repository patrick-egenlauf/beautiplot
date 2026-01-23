"""Configuration settings for beautiplot.

To change the configuration settings, use the `config` object by
importing it from `beautiplot`:

```python
>>> from beautiplot import config
```
"""

__all__ = ['config']

from pathlib import Path
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

PREAMBLE = r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{unicode-math}
\unimathsetup{math-style=ISO}
\usepackage{siunitx}
\usepackage{mathtools}
\usepackage{physics}
\usepackage{nicefrac}
\frenchspacing
\let\displaystyle\textstyle
"""


class _Config:
    """Configuration settings for beautiplot.

    This class implements the functionality exposed via
    `beautiplot.config`. It provides properties and methods to
    configure the plotting behavior, such as font size or width of
    the plot. The configuration settings are initialized during
    import, so you can change them at any time before creating a
    plot.

    Warning:
        You should never import and instantiate the `_Config` class
        directly, but always use the `config` object provided by the
        `beautiplot` module.

    Example:
        To change the width of the plot use:

        ```python
        >>> from beautiplot import config
        >>> config.width = 400
        ```
    """

    def __init__(self) -> None:
        """The configuration settings are initialized during import."""
        self._pt: float = 1 / 72.27
        self._bp: float = 1 / 72
        self._fontsize: int = 11
        self._fontfamily: str = 'serif'
        self._dpi: float = 300
        self._cmap: mcolors.Colormap = plt.get_cmap('inferno')
        self._colorbar_width: float = 10 * self._bp
        self._aspect: float = (1 + np.sqrt(5)) / 2
        self._width: float = 426.79135 * self._pt
        self._tex_preamble: str = PREAMBLE
        self._output_path: Path = Path('')
        self._margin_threshold: float = 1.0
        self._spacing_threshold: float = 6.0
        self._legend_setup: dict[str, Any] = {
            'columnspacing': 1.5,
            'handlelength': 1.5,
            'handletextpad': 0.5,
            'borderaxespad': 0.2,
        }
        self._init_matplotlib()

    @property
    def pt(self) -> float:
        """Point size in inches.

        The point size is calculated as 1/72.27.
        """
        return self._pt

    @property
    def bp(self) -> float:
        """Big point size in inches.

        The big point size is calculated as 1/72.0.
        """
        return self._bp

    @property
    def aspect(self) -> float:
        """Aspect ratio of the plot.

        The default value is the golden ratio.
        """
        return self._aspect

    @aspect.setter
    def aspect(self, value: float) -> None:
        self._aspect = value

    @property
    def cmap(self) -> mcolors.Colormap:
        """Colormap used for plotting.

        The default value is 'inferno'. You can set this to any colormap
        available in matplotlib or a custom colormap by passing a string
        or a `matplotlib.colors.Colormap` object to the
        [`set_cmap`][beautiplot._config._Config.set_cmap] method.
        """
        return self._cmap

    def set_cmap(self, value: str | mcolors.Colormap) -> None:
        """Set the colormap used for plotting.

        Args:
            value: Colormap to use.
        """
        self._cmap = plt.get_cmap(value) if isinstance(value, str) else value

    @property
    def colorbar_width(self) -> float:
        """Width of the colorbar in inches.

        The default value is 10 bp (big points), which is approximately
        0.1397 inches. When setting this value, it is multiplied by the
        `bp` size, thus for slightly wider colorbars, you can set it to
        12, which will result in a width of approximately 0.1676 inches.
        """
        return self._colorbar_width

    @colorbar_width.setter
    def colorbar_width(self, value: float) -> None:
        self._colorbar_width = value * self._bp

    @property
    def dpi(self) -> float:
        """Dots per inch.

        The default value is 300.
        """
        return self._dpi

    @dpi.setter
    def dpi(self, value: float) -> None:
        self._dpi = value

    @property
    def fontfamily(self) -> str:
        """Font family used for text in the plot.

        The default value is 'serif'.
        """
        return self._fontfamily

    @fontfamily.setter
    def fontfamily(self, value: str) -> None:
        self._fontfamily = value
        self._init_matplotlib()

    @property
    def fontsize(self) -> int:
        """Font size used for text in the plot.

        The default value is 11.
        """
        return self._fontsize

    @fontsize.setter
    def fontsize(self, value: int) -> None:
        self._fontsize = value
        self._init_matplotlib()

    @property
    def legend_setup(self) -> dict[str, Any]:
        """Configuration for the legend.

        This dictionary contains some default settings for the legend,
        such as the spacing between columns and the length of the
        handles.
        """
        return self._legend_setup

    def add_legend_setup(self, key: str, value: Any) -> None:
        """Add or update a key-value pair in the legend setup.

        Args:
            key (str): Key to add.
            value (Any): Value to add.
        """
        self._legend_setup[key] = value

    def remove_legend_setup(self, key: str) -> None:
        """Remove a key-value pair from the legend setup.

        Args:
            key (str): Key to remove.
        """
        if key in self._legend_setup:
            del self._legend_setup[key]
        else:
            raise KeyError(f"Key '{key}' not found in legend setup.")

    def empty_legend_setup(self) -> None:
        """Empty the legend setup.

        This will remove all key-value pairs from the legend setup.
        """
        self._legend_setup.clear()

    @property
    def output_path(self) -> Path:
        """Output path for the plot.

        The default value is the current directory, i.e. `.`. If the
        output path does not exist, it will be created.
        """
        return self._output_path

    @output_path.setter
    def output_path(self, value: Path) -> None:
        self._output_path = Path(value)
        if not self._output_path.exists():
            self._output_path.mkdir(parents=True, exist_ok=True)

    @property
    def margin_threshold(self) -> float:
        """Threshold for margin suggestions in bp.

        The default value is 1.0.
        """
        return self._margin_threshold

    @margin_threshold.setter
    def margin_threshold(self, value: float) -> None:
        self._margin_threshold = value

    @property
    def spacing_threshold(self) -> float:
        """Threshold for spacing suggestions in bp.

        The default value is 6.0.
        """
        return self._spacing_threshold

    @spacing_threshold.setter
    def spacing_threshold(self, value: float) -> None:
        self._spacing_threshold = value

    @property
    def tex_preamble(self) -> str:
        r"""LaTeX preamble used for the text in the plot.

        The default value is:

        ```latex
        \usepackage{amsmath}
        \usepackage{amssymb}
        \usepackage{unicode-math}
        \unimathsetup{math-style=ISO}
        \usepackage{siunitx}
        \usepackage{mathtools}
        \usepackage{physics}
        \usepackage{nicefrac}
        \frenchspacing
        \let\displaystyle\textstyle
        ```
        """
        return self._tex_preamble

    @property
    def width(self) -> float:
        r"""Width of the plot in inches.

        The default value is 5.90551 inches, which corresponds to
        426.79135 pt. You can set this to the text width of your
        document. To obtain the text width, use

        ```latex
        \the\textwidth
        ```

        in your LaTeX document. This will return the text width in pt
        and you can set the width of the plot to this value. It will
        automatically be converted to inches.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value * self._pt

    def add_usepackage(self, package: str) -> None:
        """Add a LaTeX package to the preamble.

        You can find the default preamble in the
        [`tex_preamble`][beautiplot._config._Config.tex_preamble]
        property.

        Args:
            package (str): LaTeX package to add.

        Example:
            To add the bm package to the preamble use:

            ```python
            >>> from beautiplot import config
            >>> config.add_usepackage('bm')
            ```
        """
        self._tex_preamble = (
            self._tex_preamble + rf"""\usepackage{{{package}}}""" + '\n'
        )
        self._init_matplotlib()

    def remove_usepackage(self, package: str) -> None:
        """Remove a LaTeX package from the preamble.

        You can find the default preamble in the
        [`tex_preamble`][beautiplot._config._Config.tex_preamble]
        property.

        Args:
            package (str): LaTeX package to remove.

        Example:
            To remove the amsmath package from the preamble use:

            ```python
            >>> from beautiplot import config
            >>> config.remove_usepackage('amsmath')
            ```
        """
        self._tex_preamble = self._tex_preamble.replace(
            rf"""\usepackage{{{package}}}""" + '\n', ''
        )
        self._init_matplotlib()

    def add_preamble(self, preamble: str) -> None:
        r"""Add a LaTeX preamble.

        Instead of adding a package, you can add anything to the
        preamble.

        You can find the default preamble in the
        [`tex_preamble`][beautiplot._config._Config.tex_preamble]
        property.

        Args:
            preamble (str): LaTeX preamble to add.

        Example:
            To add a different spacing to the preamble use:

            ```python
            >>> from beautiplot import config
            >>> config.add_preamble(r'\frenchspacing')
            ```
        """
        self._tex_preamble = self._tex_preamble + preamble + '\n'
        self._init_matplotlib()

    def remove_preamble(self, preamble: str) -> None:
        r"""Remove a LaTeX preamble.

        Instead of removing a package, you can remove anything from the
        preamble.

        You can find the default preamble in the
        [`tex_preamble`][beautiplot._config._Config.tex_preamble]
        property.

        Args:
            preamble (str): LaTeX preamble to remove.

        Example:
            To remove the spacing command from the preamble use:

            ```python
            >>> from beautiplot import config
            >>> config.remove_preamble(r'\frenchspacing')
            ```
        """
        self._tex_preamble = self._tex_preamble.replace(preamble + '\n', '')
        self._init_matplotlib()

    def default(self) -> None:
        """Reset the configuration settings to their default values.

        Example:
            To reset the configuration settings to their default values
            use:

            ```python
            >>> from beautiplot import config
            >>> config.default()
            ```
        """
        self._pt = 1 / 72.27
        self._bp = 1 / 72
        self._fontsize = 11
        self._fontfamily = 'serif'
        self._dpi = 300
        self._cmap = plt.get_cmap('inferno')
        self._colorbar_width = 10 * self._bp
        self._aspect = (1 + np.sqrt(5)) / 2
        self._width = 426.79135 * self._pt
        self._tex_preamble = PREAMBLE
        self._output_path = Path('')
        self._legend_setup = {
            'columnspacing': 1.5,
            'handlelength': 1.5,
            'handletextpad': 0.5,
            'borderaxespad': 0.2,
        }
        self._init_matplotlib()

    def _init_matplotlib(self) -> None:
        plt.rc('font', size=self.fontsize, family=self.fontfamily)
        plt.rc('text', usetex=True)
        plt.rc('pgf', rcfonts=False, texsystem='lualatex', preamble=self.tex_preamble)
        plt.rc('contour', linewidth=1)
        plt.style.use('tableau-colorblind10')


config = _Config()
