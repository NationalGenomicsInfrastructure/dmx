"""
THIS WILL BE SOMETHING THAT LIVES IN YGGDRASIL AND JUST IMPORTED ON YOUR FLOW.
You do not need to worry about what it does, it is here just for demonstration purposes.
It is a decorator that can be used to mark functions as steps in a data processing flow.
It allows you to specify a name for the step, which can be used for logging or tracking
purposes (feature to be implemented later in Yggdrasil).
It can be used with or without a name, and if no name is provided, it defaults to the function's name.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, Union, overload

F = TypeVar("F", bound=Callable[..., Any])


@overload  # @step
def step(fn: F, /) -> F: ...


@overload  # @step() or @step(name="x")
def step(*, name: str | None = None) -> Callable[[F], F]: ...


@overload  # @step("x")
def step(name: str, /) -> Callable[[F], F]: ...


def step(
    _maybe_fn: Union[F, str, None] = None,
    /,
    *,
    name: str | None = None,
):
    """
    Usable as:
        @step                       -> step name = function name
        @step()                     -> same
        @step("custom")             -> custom name (positional)
        @step(name="custom")        -> custom name (keyword)
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        step_name = name or fn.__name__  # name from keyword OR fallback

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)  # (no-op stub)  Add logic later

        wrapper._step_name = step_name  # type: ignore[attr-defined]
        return wrapper

    # Case: @step
    if callable(_maybe_fn):
        return decorator(_maybe_fn)
    # Case: @step("custom") --> resolve to decorator with name
    if isinstance(_maybe_fn, str) and name is None:
        name = _maybe_fn

    # Case: @step() and @step(name="custom")
    return decorator
