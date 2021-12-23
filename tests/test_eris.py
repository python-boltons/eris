"""Tests for the eris package."""

from __future__ import annotations

from eris import ErisError, Err


def test_err_method() -> None:
    """Test the Err.err() method."""
    error = ErisError("test error")
    assert Err(error).err() == error
