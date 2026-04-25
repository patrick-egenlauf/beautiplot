"""Utility functions."""

import numpy as np


def log(msg: str, *args: str | int | float, **kwargs: str | int | float) -> None:
    """Log a message.

    Args:
        msg: The message to log.
        *args: Additional arguments to format the message.
        **kwargs: Additional keyword arguments to format the message.
    """
    print('  ' + msg.format(*args, **kwargs))


def fmt_num(num: int | float | np.integer | np.floating, fmt: str = 'g') -> str:
    """Format a number as a LaTeX number.

    Args:
        num: The number to format.
        fmt: The format string.

    Returns:
        The formatted number.
    """
    return rf'\num{{{num:{fmt}}}}'
