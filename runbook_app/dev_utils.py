import os

from reflex.utils.exec import is_prod_mode


def is_dev_mode():
    if os.environ.get("DEV_MODE") or not is_prod_mode():
        return True
    return False
