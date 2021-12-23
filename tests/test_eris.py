"""Tests for the eris package."""

from __future__ import annotations

from typing import Final

from syrupy.assertion import SnapshotAssertion as Snapshot

from eris import ErisError, Err


ERROR_MSG: Final = "Something went wrong..."


def test_init_err_with_error() -> None:
    """Test the Err.err() method."""
    error = ErisError("test error")
    assert Err(error).err() == error


def test_init_err_with_string() -> None:
    """Test that instantiating an Err(foo) object, where 'foo' is a string."""
    err = Err(ERROR_MSG)
    error = err.err()
    assert error.args[0] == ERROR_MSG


def test_is_json__NO_CAUSE(snapshot: Snapshot) -> None:
    """Test the Err/Error.to_json() methods.

    NO ErisError chain and NO 'caused by' exceptions.
    """
    err = Err(ERROR_MSG)
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
        err = Err(ERROR_MSG).chain(zero_div_error)
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
            err = Err(ERROR_MSG).chain(rt_error)
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
    err1 = Err("Some FOO error has occurred.")
    err2 = Err("Some BAR error has occurred.").chain(err1)
    assert snapshot == err2.to_json()
