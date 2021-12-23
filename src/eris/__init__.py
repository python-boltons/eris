"""eris package

The Greek Goddess of Strife and Discord... The better way to handle, trace, and
log errors in Python.
"""

import logging as _logging

from ._errors import ErisError, ErisErrorChain, ErisErrorDict
from ._result import Err, LazyResult, Ok, Result, return_lazy_result


__all__ = [
    "ErisError",
    "ErisErrorChain",
    "ErisErrorDict",
    "Err",
    "LazyResult",
    "Ok",
    "Result",
    "return_lazy_result",
]

__author__ = "Bryan M Bugyi"
__email__ = "bryanbugyi34@gmail.com"
__version__ = "0.1.2"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
