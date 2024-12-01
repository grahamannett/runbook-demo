from typing import Callable

import reflex as rx


def signin(on_submit_signin: Callable):
    return rx.box(
        rx.heading("Enter App Password"),
        rx.form(
            rx.input(
                placeholder="app password",
            ),
            on_submit=on_submit_signin,
        ),
    )
