import re
from .expression import (
    Expression,
    SequenceExpression,
    OrExpression,
    LiteralExpression,
    RegularExpression,
    GroupExpression,
    CardinalityType,
)


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

    If the name is all uppercase, it is returned as is to account for terminal rules.

    Example: "DefinitionBodyItem" → "definition_body_item"
    Example: "QUAL_NAME" → "QUAL_NAME"
    """
    # Insert underscore between lowercase and uppercase letters
    if name.isupper():
        return name
    s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # Convert the entire string to lowercase
    return s1.lower()


def single_to_double_quotes(s: str) -> str:
    """
    Converts a string encased in single quotes to one encased in double quotes.
    Also handles escaping of internal quotes:
    - Internal double quotes are escaped with backslashes
    - Internal escaped single quotes are converted to just single quotes

    Examples:
        "'hello'" → "\"hello\""
        "'hello \"world\"'" → "\"hello \\\"world\\\"\""
        "'don\\'t worry'" → "\"don't worry\""

    Args:
        s: A string encased in single quotes (e.g., "'text'")

    Returns:
        The string content encased in double quotes with proper escaping
    """
    # Check if the string starts and ends with single quotes
    if s.startswith("'") and s.endswith("'"):
        # Extract content between single quotes
        content = s[1:-1]
        # Replace internal double quotes with escaped double quotes
        content = content.replace('"', '\\"')
        # Replace internal escaped single quotes with just single quotes
        content = content.replace("\\'", "'")
        return f'"{content}"'
    else:
        # Return original if not properly encased in single quotes
        return s


def strip_double_quotes(s: str) -> str:
    """
    Removes surrounding double quotes from a string if present.

    Args:
        s: A string that may be encased in double quotes

    Returns:
        The string with surrounding double quotes removed

    Examples:
        "\"hello\"" → "hello"
        "hello" → "hello"
    """
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


def character_range_regex(start_char: str, end_char: str) -> str:
    """
    Creates a Lark-compatible regular expression string representing a character range.

    Args:
        start_char: The starting character of the range
        end_char: The ending character of the range

    Returns:
        A string representing a regular expression for the character range

    Example:
        character_range_regex("a", "z") returns "/[a-z]/"
    """
    # Ensure inputs are single characters
    start_char = strip_double_quotes(start_char)
    end_char = strip_double_quotes(end_char)
    if len(start_char) != 1 or len(end_char) != 1:
        raise ValueError("Both start_char and end_char must be single characters")

    pattern = re.compile(f"[{start_char}-{end_char}]")
    return pattern.pattern


def wildcard_regex(start_char: str, end_char: str) -> str:
    """
    Creates a Lark-compatible regular expression string representing a character range.

    Args:
        start_char: The starting character of the range
        end_char: The ending character of the range

    Returns:
        A string representing a regular expression for the character range

    Example:
        character_range_regex("a", "z") returns "/[a.z]/"
    """
    # Ensure inputs are single characters
    start_char = strip_double_quotes(start_char)
    end_char = strip_double_quotes(end_char)
    if len(start_char) != 1 or len(end_char) != 1:
        raise ValueError("Both start_char and end_char must be single characters")

    pattern = re.compile(f"[{start_char}.{end_char}]")
    return pattern.pattern


def escape_regex_chars(s: str) -> str:
    """
    Escapes characters that have special meaning in regular expressions.

    Args:
        s: The string to escape

    Returns:
        The string with special regex characters escaped

    Example:
        escape_regex_chars("[test]") returns "\\[test\\]"
    """
    # Characters that need to be escaped in regex patterns
    special_chars = r"/[](){}?*+|^$."

    # Escape each special character with a backslash
    result = ""
    for char in s:
        if char in special_chars:
            result += "\\" + char
        else:
            result += char

    return result


def until_regex(start: str, end: str) -> str:
    """
    Creates a Lark-compatible regular expression string representing a starting and ending literal.

    Args:
        start: The starting literal
        end: The ending literal

    Returns:
        A string representing a regular expression in Lark

    Example:
        character_range_regex("a", "z") returns "/[a.*z]/"
    """
    start = escape_regex_chars(strip_double_quotes(start))
    end = escape_regex_chars(strip_double_quotes(end))

    # Create the regex pattern
    return f"[{start}.*{end}]"


# Check if the expression is negated and contains only LiteralExpressions or RegularExpressions
def contains_only_literals(expr: Expression):
    if isinstance(expr, LiteralExpression) or isinstance(expr, RegularExpression):
        return True
    elif isinstance(expr, SequenceExpression) or isinstance(expr, OrExpression):
        return all(contains_only_literals(e) for e in expr.expressions)
    elif isinstance(expr, GroupExpression):
        return contains_only_literals(expr.expression)
    else:
        return False


def expression_to_regex(expr: Expression) -> re.Pattern:
    """
    Converts an Expression object to a Python re pattern object.
    Only works for expressions where all atomic expressions are literals or regular expressions.

    Args:
        expr: An Expression object to convert

    Returns:
        A compiled regular expression pattern object

    Raises:
        ValueError: If the expression contains atomic expressions that are not literals or regular expressions
    """
    if not contains_only_literals(expr):
        raise ValueError(
            "Expression must only contain literals and regular expressions"
        )

    pattern_str = _build_regex_pattern(expr)
    return re.compile(pattern_str)


def _build_regex_pattern(expr: Expression) -> str:
    """
    Recursively builds a regex pattern string from an Expression.

    Args:
        expr: The Expression to convert

    Returns:
        A string representation of a regular expression
    """
    if isinstance(expr, LiteralExpression):
        # Escape any regex special characters in the literal
        return re.escape(strip_double_quotes(expr.value))

    elif isinstance(expr, RegularExpression):
        # Regular expressions are assumed to already be valid regex patterns
        # Remove any leading/trailing slashes if present (common in some regex formats)
        pattern = expr.value
        if pattern.startswith("/") and pattern.endswith("/"):
            pattern = pattern[1:-1]
        return pattern

    elif isinstance(expr, SequenceExpression):
        # Join all subexpressions with no delimiter (AND operation)
        return "".join(_build_regex_pattern(e) for e in expr.expressions)

    elif isinstance(expr, OrExpression):
        # Join all subexpressions with | (OR operation)
        return "|".join(f"(?:{_build_regex_pattern(e)})" for e in expr.expressions)

    elif isinstance(expr, GroupExpression):
        # Handle groups with their cardinality and negation
        inner_pattern = _build_regex_pattern(expr.expression)

        # Handle negation if present
        if expr.negated:
            # Negative lookahead to ensure the pattern doesn't match
            pattern = f"(?!{inner_pattern})"
        else:
            # Group the pattern
            pattern = f"(?:{inner_pattern})"

        # Apply cardinality if specified
        if expr.cardinality_type is not None:
            if expr.cardinality_type == CardinalityType.OPTIONAL:
                pattern += "?"
            elif expr.cardinality_type == CardinalityType.AT_LEAST_ONE:
                pattern += "+"
            elif expr.cardinality_type == CardinalityType.ZERO_OR_MORE:
                pattern += "*"

        return pattern
    else:
        raise ValueError(f"Unsupported expression type: {type(expr)}")
