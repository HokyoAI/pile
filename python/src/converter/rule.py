from dataclasses import dataclass, field
from typing import ClassVar
from .utils import REQUIRED, DEFAULT_RETURN_TYPE, DefaultReturnType
from .expression import Expression


@dataclass
class XTextRule:
    # Class variable to track required fields
    _required_fields: ClassVar[set] = set()

    is_override: bool = False
    is_final: bool = False
    is_deprecated: bool = False
    is_exported: bool = False

    is_terminal: bool = False
    is_enum: bool = False
    is_fragment: bool = False

    name: str = field(default=REQUIRED)

    body: Expression = field(default=REQUIRED)

    # the qualified name is split
    return_type: list[str] | DefaultReturnType = field(default=DEFAULT_RETURN_TYPE)

    def __post_init__(self):
        """Initialize _required_fields and replace REQUIRED with None"""
        # Reset required fields
        self._required_fields = set()

        # Find all fields marked with REQUIRED sentinel and replace with None
        for name, value in self.__dict__.items():
            if value is REQUIRED:
                self._required_fields.add(name)
                setattr(self, name, None)

    def validate(self) -> bool:
        """Check if all required fields have been set."""
        missing = []
        for field_name in self._required_fields:
            if getattr(self, field_name) is None:
                missing.append(field_name)

        if missing:
            raise ValueError(f"Required fields not set: {', '.join(missing)}")
        return True

    def is_complete(self) -> bool:
        """Non-raising version to check if object is complete."""
        return all(
            getattr(self, field_name) is not None
            for field_name in self._required_fields
        )
