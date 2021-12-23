"""Tests for the eris package."""

from __future__ import annotations

from typing import Any, Final, Optional

from pytest import mark
from syrupy.assertion import SnapshotAssertion as Snapshot

from eris import ErisError, Err, Ok, Result


params = mark.parametrize

DEFAULT_FOOBAR: Final = "FOOBAR"
ERROR_MSG: Final = "Something went wrong..."


class CustomErisError(ErisError):
    """Custom Exception Type."""

    def __init__(
        self, *args: Any, foobar: str = DEFAULT_FOOBAR, **kwargs: Any
    ) -> None:
        self.foobar = foobar
        super().__init__(*args, **kwargs)


def fail_with_custom_error(foobar: str = None) -> Result[int, CustomErisError]:
    """Helper function used to test that custom ErisError types work."""
    try:
        x = 1 / 0
        print(x)
    except ZeroDivisionError as zero_div_error:
        if foobar is None:
            custom_eris_error = CustomErisError(ERROR_MSG)
        else:
            custom_eris_error = CustomErisError(ERROR_MSG, foobar=foobar)

        err: Err[int, CustomErisError] = Err(custom_eris_error)
        return err.chain(zero_div_error)
    else:
        return Ok(0)


def test_init_err_with_error() -> None:
    """Test the Err.err() method."""
    error = ErisError("test error")
    assert Err(error).err() == error


def test_init_err_with_string() -> None:
    """Test that instantiating an Err(foo) object, where 'foo' is a string."""
    err: Err[Any, ErisError] = Err(ERROR_MSG)
    error = err.err()
    assert error.args[0] == ERROR_MSG


def test_is_json__NO_CAUSE(snapshot: Snapshot) -> None:
    """Test the Err/Error.to_json() methods.

    NO ErisError chain and NO 'caused by' exceptions.
    """
    err: Err[Any, ErisError] = Err(ERROR_MSG)
    error = err.err()
    assert snapshot == error.to_json()


def test_is_json__ONE_CAUSE(snapshot: Snapshot) -> None:
    """Test the Err/Error.to_json() methods.

    NO ErisError chain and ONE 'caused by' exception.
    """
    try:
        x = 1 / 0
        print(x)
    except ZeroDivisionError as zero_div_error:
        err: Err = Err(ERROR_MSG).chain(zero_div_error)
        assert snapshot == err.to_json()


def test_is_json__TWO_CAUSE(snapshot: Snapshot) -> None:
    """Test the Err/Error.to_json() methods.

    NO ErisError chain and TWO 'caused by' exceptions.
    """
    try:
        x = 1 / 0
        print(x)
    except ZeroDivisionError as zero_div_error:
        try:
            raise RuntimeError(
                "Why would we divide by zero?"
            ) from zero_div_error
        except RuntimeError as rt_error:
            err: Err = Err(ERROR_MSG).chain(rt_error)
            assert snapshot == err.to_json()


def test_is_json__TWO_CAUSE_AND_RAISE_SELF(snapshot: Snapshot) -> None:
    """Test the Err/Error.to_json() methods.

    NO ErisError chain and TWO 'caused by' exceptions. This test case calls
    Error.to_json() after catching an Error exception.
    """
    try:
        x = 1 / 0
        print(x)
    except ZeroDivisionError as zero_div_error:
        try:
            raise RuntimeError(
                "Why would we divide by zero?"
            ) from zero_div_error
        except RuntimeError as rt_error:
            error = ErisError(ERROR_MSG)
            try:
                raise error from rt_error
            except ErisError as eris_error:
                assert snapshot == eris_error.to_json()


def test_is_json__CHAIN(snapshot: Snapshot) -> None:
    """Test the Err/Error.to_json() methods.

    Chain multiple Error objects together.
    """
    err: Err[Any, ErisError] = Err("Some BAR error has occurred.")
    other_err: Err[Any, ErisError] = Err(ERROR_MSG)
    err = err.chain(other_err)

    assert snapshot == err.to_json()


@params("foobar,expected", [(None, DEFAULT_FOOBAR), ("bazbar", "bazbar")])
def test_custom_error(foobar: Optional[str], expected: str) -> None:
    """Tests that we can subclass ErisError."""
    my_result = fail_with_custom_error(foobar=foobar)

    assert isinstance(my_result, Err)
    err = my_result.err()
    assert err.foobar == expected
