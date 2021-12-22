"""eris package

The Greek Goddess of Strife and Discord... The better way to handle, trace, and
log errors in Python.
"""

import logging as _logging

from ._errors import Error, chain_errors


__all__ = ["Error", "chain_errors"]

__author__ = "Bryan M Bugyi"
__email__ = "bryanbugyi34@gmail.com"
__version__ = "0.0.1"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
