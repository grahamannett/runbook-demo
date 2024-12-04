import os
from contextlib import asynccontextmanager
from functools import wraps
from typing import Callable, Sequence

import reflex as rx
from reflex.utils.exec import is_prod_mode

from runbook_app.components.auth_signin import signin


def is_dev_mode():
    if os.environ.get("DEV_MODE") or not is_prod_mode():
        return True
    return False


def make_require_login(chat_state: type["ChatState"]) -> Callable:
    def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
        if is_dev_mode():
            return page

        @wraps(page)
        def protected_page() -> rx.Component:
            return rx.box(
                rx.cond(
                    chat_state.is_hydrated,
                    rx.cond(
                        chat_state.valid_session,
                        page(),
                        signin(
                            on_submit_signin=chat_state.handle_login_form,
                        ),
                    ),
                    rx.spinner(),
                ),
            )

        return protected_page

    return require_login


@asynccontextmanager
async def proc_ctx(state: type[rx.State], with_fn: Sequence[Callable] = []) -> type[rx.State]:  # type: ignore[type-arg]
    """
    An asynchronous context manager for processing chat state with optional functions.

    This context manager wraps the chat state and executes a sequence of provided
    functions both before and after the main operation. It ensures that the chat
    state is properly managed and any cleanup operations are performed.

    Args:
        state (rx.State): The chat state to be managed.
        with_fn (Sequence[Callable], optional): A sequence of callable functions
            to be executed before and after the main operation. Defaults to an empty list.

    Yields:
        rx.State: The managed chat state.

    Example:
        async with proc_ctx(state, [func1, func2]) as state:
            # Perform operations with the managed chat state
    """

    def call_with() -> None:
        _ = [fn() for fn in with_fn]

    async with state:
        call_with()
        try:
            yield state
        finally:
            call_with()
