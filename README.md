# Welcome to beautiplot

[![CI](https://github.com/patrick-egenlauf/beautiplot/actions/workflows/main.yml/badge.svg)](https://github.com/patrick-egenlauf/beautiplot/actions/workflows/main.yml?query=branch%3Amain)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/beautiplot.svg)](https://pypi.python.org/pypi/beautiplot)

**Beautiful, Consistent, and Reproducible Scientific Plots with Python.**

Beautiplot is a Python library for beautiful, consistent, and publication-ready scientific plots. Built on [Matplotlib](https://matplotlib.org/stable/), it offers high-level functions, reproducible styles, and easy customization - perfect for researchers, students, and engineers.

## Features

- Unified, professional style out of the box
- High-level functions for subplots, colorbars, labels, and more
- Publication-quality sizing and formatting
- Centralized configuration for reproducibility
- Fully customizable and extensible

## Installation

The package can be installed from PyPI, either via pip

``` { .shell .copy }
pip install beautiplot
```

or via [uv](https://docs.astral.sh/uv/)

``` { .shell .copy }
uv add beautiplot
```

## Quick Example

```python
import beautiplot.plot as bp
import numpy as np

t = np.linspace(0, 10, 1000)
y = 5 * np.exp(-t / 2) * np.cos(2 * np.pi * t)
fig, ax = bp.newfig(left=40, bottom=35)
ax.plot(t, y, label='Damped Oscillation')
ax.set_xlabel('Time $t$ / s')
ax.set_ylabel('Amplitude $A(t)$ / cm')
bp.legend(ax)
bp.save_figure(fig, 'damped_oscillation.pdf')
```

## Documentation

For a full overview, visit the [documentation](https://patrick-egenlauf.github.io/beautiplot/).

- **[Getting Started](https://patrick-egenlauf.github.io/beautiplot/getting_started/):** Install `beautiplot` and make your first plot.
- **[Tutorials](https://patrick-egenlauf.github.io/beautiplot/tutorials/):** Step-by-step guides for common tasks.
- **[API Reference](https://patrick-egenlauf.github.io/beautiplot/reference/beautiplot/):** Detailed documentation for all functions.

**Make your science beautiful, reproducible, and effortless - with beautiplot!**
