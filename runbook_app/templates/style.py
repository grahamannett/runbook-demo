from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator


class ABCStyle(Mapping):
    """

    cannot remember exactly why this is necessary but I am pretty sure it is to allow the Style
    subclasses to be used in various ways, e.g.


    class SharedStyle(BaseStyle):
        default = {...example kwargs...}

    can also do:

    - SharedStyle = BaseStyle(**{...example kwargs...})
    or
    - SharedStyle = BaseStyle(default={...example kwargs...})


    """

    default: dict[str, Any] = dict()


@dataclass
class BaseStyle(ABCStyle):
    """Abstract base class for style definitions across the application.

    This class provides a consistent way to define styles and behaves like a dictionary.
    The style values can be accessed directly from the instance.

    Example:
        >>> style = BaseStyle(width="100%", height="100%")
        >>> style["width"]  # returns "100%"
        >>> style.update(padding="1em")
    """

    default: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, *args, **kwargs):
        """Initialize style with optional values.

        Supports three initialization patterns:
        1. BaseStyle(key="value", ...)
        2. BaseStyle(default={"key": "value", ...})
        3. BaseStyle(**existing_style)
        """
        super().__init__()

        if not kwargs:
            return

        if len(args) > 0:
            raise TypeError(f"{self.__class__.__name__} only accepts keyword arguments")

        self.default = {
            **self.default,  # might need to do getattr(self, "default", {}) if not self.default
            **kwargs.get("default", kwargs),
        }

    def __getitem__(self, key: str) -> Any:
        """Access style values directly from the instance."""
        return self.default[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set style values directly from the instance."""
        self.default[key] = value

    def __iter__(self) -> Iterator[str]:
        """Iterate over style keys."""
        return iter(self.default)

    def __len__(self) -> int:
        """Get number of style properties."""
        return len(self.default)

    def update(self: "BaseStyle", **kwargs) -> "BaseStyle":
        """Update the style dictionary with new values.

        Args:
            **kwargs: Key-value pairs to update in the style dictionary

        Returns:
            Self for method chaining
        """
        self.default.update(kwargs)
        return self
