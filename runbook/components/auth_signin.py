from typing import Callable

import reflex as rx


def signin(on_submit_signin: Callable):
    return rx.center(
        rx.vstack(
            rx.spacer(),
            rx.spacer(),
            rx.heading("enter password"),
            rx.form(
                rx.box(
                    rx.hstack(
                        rx.input(
                            placeholder="app password",
                            name="app_password",
                        ),
                        rx.button("submit", type="submit"),
                    ),
                ),
                on_submit=on_submit_signin,
            ),
        ),
    )
