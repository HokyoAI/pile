class Required:
    """Sentinel class to mark required fields that aren't provided at init time."""

    pass


REQUIRED = Required()


class DefaultReturnType:
    """Sentinel class to mark rules that don't have a return type."""

    pass


DEFAULT_RETURN_TYPE = DefaultReturnType()
