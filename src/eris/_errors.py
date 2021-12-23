"""Custom Exceptions live here."""

from __future__ import annotations

import traceback
from typing import (
    Final,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

from ion import efill
from metaman import Inspector, cname
from typist import E, T


Null = Literal["null"]
Nullable = Union[Null, T]
ErrorChain = List["ErrorDict"]
ExcInfoTuple = Tuple[str, str, Nullable[str]]

FIRST_EXC_IS_WRONG_TYPE: Final = (
    "Logic error. The first exception returned by iterating over this"
    " exception should be THIS exception."
)
NULL: Final = "null"


class ExcInfo(TypedDict):
    """Represents a single exception."""

    exc_type: str
    exc_value: str
    exc_msg: str


class ErrorDict(TypedDict):
    """An Error type represented as a dictionary."""

    # exception info
    exc_info: ExcInfo

    # metadata
    lineno: int
    module_name: str
    func_name: str
    file_name: str
    lines: List[str]

    # optional traceback stack + exception that caused it
    stack: Nullable[List[str]]
    caused_by: Nullable[List[ExcInfoTuple]]


class Error(Exception):
    """Custom general-purpose exception."""

    def __init__(self, emsg: str, up: int = 0) -> None:
        self.inspector = Inspector(up=up + 1)
        super().__init__(emsg)

    def __str__(self) -> str:  # noqa: D105
        return self.__repr__()

    def __repr__(self) -> str:  # noqa: D105
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

    def __iter__(self) -> Iterator["BaseException"]:  # noqa: D105
        yield self

        e = self.__cause__
        while e:
            yield e
            e = e.__cause__

    def chain(self, other: Exception) -> "Error":
        """Chains this exception to another."""
        return chain_errors(self, other)

    def to_json(self) -> ErrorChain:
        """Converts this error into a list of dictionaries.

        This list is JSON serializable and is composed of data on this
        exception and any that are chained to it.

        NOTE: The list is sorted from last-to-first exception to be raised
        (i.e. this exception, the exception that caused this exception,
        etc...).
        """
        result = []
        last_stack: Optional[List[str]] = None
        last_caused_by: Optional[List[ExcInfoTuple]] = None
        for error in self:
            if isinstance(error, Error):
                caused_by = last_caused_by = []
                stack = last_stack = []

                exc_info: ExcInfo = dict(
                    exc_type=str(type(error)),
                    exc_value=str(error),
                    exc_msg=error.args[0],
                )
                error_dict: ErrorDict = dict(
                    exc_info=exc_info,
                    lineno=error.inspector.line_number,
                    module_name=error.inspector.module_name,
                    func_name=error.inspector.function_name,
                    file_name=error.inspector.file_name,
                    # lines=error.inspector.lines,
                    lines=[],
                    stack=stack,
                    caused_by=caused_by,
                )
                result.append(error_dict)
            else:
                assert last_stack is not None, FIRST_EXC_IS_WRONG_TYPE
                assert last_caused_by is not None, FIRST_EXC_IS_WRONG_TYPE

                exc_info_tuple: ExcInfoTuple = (
                    str(type(error)),
                    str(error),
                    str(error.args[0]) if error.args else NULL,
                )
                last_caused_by.append(exc_info_tuple)

                if tb := error.__traceback__:
                    last_stack.extend(traceback.extract_tb(tb).format())

        return result


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
