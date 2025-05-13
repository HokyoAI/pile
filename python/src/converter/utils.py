import re


class XTextCurrent:
    pass


XTEXT_CURRENT = XTextCurrent()


class NonParsing:
    """Sentinel class to mark non-parsing elements."""

    pass

    def __str__(self):
        return ""


NON_PARSING = NonParsing()


class Required:
    """Sentinel class to mark required fields that aren't provided at init time."""

    pass


REQUIRED = Required()


class DefaultReturnType:
    """Sentinel class to mark rules that don't have a return type."""

    pass


DEFAULT_RETURN_TYPE = DefaultReturnType()


def pascal_to_snake_case(name: str) -> str:
    """
    Converts an Xtext rule name (CamelCase or PascalCase)
    to a Lark rule name (snake_case and lowercase).

    Example: "DefinitionBodyItem" → "definition_body_item"
    """
    # Insert underscore between lowercase and uppercase letters
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # Convert the entire string to lowercase
    return s1.lower()
