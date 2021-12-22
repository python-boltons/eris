"""Custom Exceptions live here."""

from __future__ import annotations

from typing import Iterator, Optional

from ion import efill
from metaman import Inspector, cname
from typist import E


class Error(Exception):
    """Custom general-purpose exception."""

    def __init__(
        self, emsg: str, cause: Exception = None, up: int = 0
    ) -> None:

        chain_errors(self, cause)
        self.inspector = Inspector(up=up + 1)
        super().__init__(emsg)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return self._repr()

    def _repr(self, width: int = 80) -> str:
        """
        Format error to width.  If width is None, return string suitable for
        traceback.
        """
        super_str = super().__str__()

        emsg = efill(super_str, width, indent=2)
        return "{}::{}::{}::{}{{\n{}\n}}".format(
            cname(self),
            self.inspector.module_name,
            self.inspector.function_name,
            self.inspector.line_number,
            emsg,
        )

    def __iter__(self) -> Iterator[BaseException]:
        yield self

        e = self.__cause__
        while e:
            yield e
            e = e.__cause__


def chain_errors(e1: E, e2: Optional[Exception]) -> E:
    """Chain two exceptions together.

    This is the functional equivalent to ``raise e1 from e2``.

    Args:
        e1: An exception.
        e2: The exception we want to chain to ``e2``.

    Returns:
        ``e1`` after chaining ``e2`` to it.
    """
    e: BaseException = e1
    cause = e.__cause__
    while cause:
        e = cause
        cause = e.__cause__
    e.__cause__ = e2
    return e1
