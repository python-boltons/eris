"""Result Return Type / Error-Handling Implementation

This module implements an error-handling model that is heavily influenced by
the Rust programming language's Result type [1] and an article titled
"Python: better typed than you think" [2]. This model is used as the default
error-handling model in some modern programming languages (e.g. Go and Rust),
but has also been used successfully for years by functional programming
languages (e.g. Haskell).

The model revolves around the use of the Result type, which, in turn, is
always either an Ok instance or an Err instance.

[1]: https://doc.rust-lang.org/std/result
[2]: https://beepb00p.xyz/mypy-error-handling.html#coderef-throw_exc

Examples:
    Consider a function which has a known error-state. If an error does occur,
    we want to propagate the error to the caller somehow. We can rely on
    Python's built-in exceptions to handle this propagation, like so:

        def do_stuff() -> str:
            # do some stuff which sets the 'status' variable
            if status == SUCCESS:
                return "SUCCESS!"
            else:
                raise SomeError("<Error Context>")

    This method couples the caller to the `do_stuff()` function's
    implementation, however, since the caller MUST know that `do_stuff()` might
    raise a SomeError exeption before calling `do_stuff()`. Furthermore, if the
    caller does NOT handle this exception, there is no warning; SomeError will
    continue to propagate up the call-stack until it crashes the program.

    This module attempts to offer a safer approach. Using the `Result` return
    type, we might define `do_stuff()` like this:

        def do_stuff() -> Result[str, SomeError]:
            # do some stuff which sets the 'status' variable
            if status == SUCCESS:
                return Ok("SUCCESS!")
            else:
                e = SomeError("<Error Context>")
                return Err(e)

    This approach has the benefit of being type-safe: A function that calls
    `do_stuff()` MUST check for errors. This is enforced by type-checking tools
    like mypy, but is also made fairly obvious to the caller given the return
    type of `do_stuff()`. To demonstrate, let us now consider how a client
    might go about calling `do_stuff()`:

        def main() -> int:
            msg_result = do_stuff()
            if isinstance(msg_result, Err):
                e = msg_result.err()
                logger.error("An error occurred while doing stuff: %r", e)
                return 1

            msg = msg_result.ok()
            logger.info(msg)
            return 0

    Some might say a downside of this approach is that it requires you to write
    a lot of boilerplate error-handling logic. I would argue that this is yet
    another benefit of this approach, since dangerous code _should_ look
    dangerous. With that said, if we just want to crash the program on error,
    we could shorten the above `main()` function like so:

        def main() -> int:
            msg = do_stuff().unwrap()  # raises SomeError if an error occurs
            logger.info(msg)
            return 0
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    NoReturn,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from ._errors import ErisError, ErisErrorChain


T = TypeVar("T")
E = TypeVar("E", bound=ErisError)
ErrType = TypeVar("ErrType", bound="Err")


class AbstractResult(ABC, Generic[T, E]):
    """This class defines what a Result object looks like."""

    def __bool__(self) -> NoReturn:
        """Called implicitly on `bool(ok_or_err)`.

        We raise a ValueError here to prevent Ok/Err objects from being
        evaluated as bools, which can make it easy to forget to check for
        errors and make it seem like a predicate (i.e. a function that returns
        a bool) always returns True.
        """
        raise ValueError(
            f"{self.__class__.__name__} object cannot be evaluated as a"
            " boolean. This is probably a bug in your code. Make sure you are"
            " either explicitly checking for Err results or using one of the"
            f" `Result.unwrap*()` methods:  {self!r}"
        )

    @abstractmethod
    def err(self) -> Optional[E]:
        """Returns None if successful or an Exception type otherwise."""

    @abstractmethod
    def unwrap(self) -> T:
        """Returns real return type or raises an exception if unsuccessful."""

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns real return type if successful or ``default`` otherwise."""

    @abstractmethod
    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Returns real return type if successful or ``op(e)`` otherwise."""


@dataclass(frozen=True)
class Ok(AbstractResult[T, E]):
    """Ok result type.

    A value that indicates success and which stores arbitrary data for the
    return value.
    """

    _value: T

    @staticmethod
    def err() -> None:  # noqa: D102
        return None

    def ok(self) -> T:  # noqa: D102
        return self._value

    def unwrap(self) -> T:  # noqa: D102
        return self.ok()

    def unwrap_or(self, default: T) -> T:  # noqa: D102
        return self.ok()

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:  # noqa: D102
        return self.ok()


@dataclass
class Err(AbstractResult[T, E]):
    """Err result type.

    A value that signifies failure and which stores arbitrary data for the
    error.
    """

    # `error_spec` is used to construct `_error` and is then thrown away
    #
    # WARNING: If `error_spec` is a string, then the type variable `E` _must_
    # be `ErisError`!
    error_spec: InitVar[Union[str, E]]
    _error: E = field(init=False)

    # `up` is used to control what set of metadata we see when inspecting an
    # ErisError. Useful when writing functions that are meant to wrap the Err
    # type.
    #
    # WARNING: `up` can _only_ be provided when `error_spec` is a string, since
    # this argument is passed to ErisError to construct it. This argument has
    # no effect otherwise (since assertions are probably a bad idea inside of
    # error-handling logic).
    up: InitVar[int] = 0

    def __post_init__(self, error_spec: Union[str, E], up: int) -> None:
        """Special `dataclasses.dataclass` method.

        We perform the following tasks at post-init time:
            * Set the `_error` attribute.
        """
        if isinstance(error_spec, str):
            self._error = cast(E, ErisError(error_spec, up=up + 2))
        else:
            self._error = error_spec

    def err(self) -> E:  # noqa: D102
        return self._error

    def unwrap(self) -> NoReturn:  # noqa: D102
        raise self.err()

    def unwrap_or(self, default: T) -> T:  # noqa: D102
        return default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:  # noqa: D102
        return op(self.err())

    def chain(self: ErrType, exc_or_err: Union[Exception, Err]) -> ErrType:
        """Wraps another Exception object with this Exception object."""
        if isinstance(exc_or_err, Exception):
            other_exception = exc_or_err
        else:
            other_exception = exc_or_err.err()

        self.err().chain(other_exception)
        return self

    def to_json(self) -> ErisErrorChain:
        """A thin wrapper around ErisError.to_json()."""
        return self.err().to_json()


# The 'Result' return type is used to implement an error-handling model heavily
# influenced by that used by the Rust programming language
# (see https://doc.rust-lang.org/book/ch09-00-error-handling.html).
Result = Union[Ok[T, E], Err[T, E]]


def return_lazy_result(
    func: Callable[..., Result[T, E]]
) -> Callable[..., "LazyResult[T, E]"]:
    """Converts the return type of a function from result to a "lazy" result.

    In order to fetch the real return type from lazy_result, you must call
    lazy_result.result() or any other valid Result method [e.g.
    lazy_result.unwrap()].

    This decorator is useful when dealing with functions that return
    Result[None] (i.e. functions that are used soley for their
    side-effects), since it makes it harder to ignore potential errors.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> LazyResult[T, E]:
        return LazyResult(func, *args, **kwargs)

    return wrapper


class LazyResult(AbstractResult[T, E]):
    """See `help(return_lazy_result)`."""

    def __init__(
        self, func: Callable[..., Result[T, E]], *args: Any, **kwargs: Any
    ) -> None:
        self._func = func
        self._args: Tuple[Any, ...] = args
        self._kwargs: Dict[str, Any] = kwargs

        self._result: Optional[Result[T, E]] = None

    def result(self) -> Result[T, E]:
        """Retrieve the Result object corresponding with this LazyResult.

        Calls the function corresponding with this LazyResult (this function
        will only be called once, even if this method is called multiple times)
        and returns the same Result returned by that function.
        """
        if self._result is None:
            self._result = self._func(*self._args, **self._kwargs)
        return self._result

    def err(self) -> Optional[E]:  # noqa: D102
        return self.result().err()

    def unwrap(self) -> T:  # noqa: D102
        return self.result().unwrap()

    def unwrap_or(self, default: T) -> T:  # noqa: D102
        return self.result().unwrap_or(default)

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:  # noqa: D102
        return self.result().unwrap_or_else(op)
