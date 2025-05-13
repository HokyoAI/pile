from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import re


class CardinalityType(Enum):
    OPTIONAL = "?"
    AT_LEAST_ONE = "+"
    ZERO_OR_MORE = "*"


@dataclass
class DataType:
    namespace: str
    qualified_name: list[str]


@dataclass
class Expression:
    """Base expression class"""

    pass


@dataclass
class AtomicExpression(Expression):
    """Leaf node representing a basic expression"""

    value: str

    def __str__(self):
        return str(self.value)


@dataclass
class RegularExpression(AtomicExpression):
    """Represents a regular expression"""

    pass


@dataclass
class RuleCallExpression(AtomicExpression):
    """Represents a rule call expression"""

    pass


@dataclass
class LiteralExpression(AtomicExpression):
    """Represents a literal expression"""

    pass


@dataclass
class SequenceExpression(Expression):
    """Represents a sequence of expressions (AND)"""

    expressions: List[Expression]

    def __str__(self):
        return " ".join(str(expr) for expr in self.expressions)


@dataclass
class OrExpression(Expression):
    """Represents a disjunction of expressions (OR)"""

    expressions: List[Expression]

    def __str__(self):
        return " | ".join(str(expr) for expr in self.expressions)


@dataclass
class GroupExpression(Expression):
    """Represents a group of expressions in parentheses"""

    expression: Expression
    negated: bool = False
    cardinality_type: Optional[CardinalityType] = None

    def __str__(self):
        # Check if the expression is negated and contains only LiteralExpressions
        def contains_only_literals(expr):
            if isinstance(expr, LiteralExpression):
                return True
            elif isinstance(expr, SequenceExpression) or isinstance(expr, OrExpression):
                return all(contains_only_literals(e) for e in expr.expressions)
            elif isinstance(expr, GroupExpression):
                return contains_only_literals(expr.expression)
            else:
                return False

        # Special handling for negated expressions containing only literals
        if self.negated and contains_only_literals(self.expression):
            # Handle negated literals by creating a regex expression
            # For example: !("a" | "b") becomes /[^ab]/
            literals = []

            def extract_literals(expr):
                if isinstance(expr, LiteralExpression):
                    # Strip quotes from literal values
                    val = expr.value.strip("\"'")
                    literals.append(val)
                elif isinstance(expr, SequenceExpression) or isinstance(
                    expr, OrExpression
                ):
                    for e in expr.expressions:
                        extract_literals(e)
                elif isinstance(expr, GroupExpression):
                    extract_literals(expr.expression)

            extract_literals(self.expression)

            if literals:
                # Escape special regex characters
                escaped_literals = [re.escape(lit) for lit in literals]
                regex_content = "".join(escaped_literals)

                # Create negated character class
                regex_expr = f"/[^{regex_content}]/"

                # Add cardinality if present
                if self.cardinality_type is not None:
                    regex_expr = f"{regex_expr}{self.cardinality_type.value}"

                return regex_expr

        result = f"{'!' if self.negated else ''}({str(self.expression)})"
        if self.cardinality_type is not None:
            result += f"{self.cardinality_type.value}"
        return result


@dataclass
class NameResolution:
    rule_calls: List[RuleCallExpression]
    data_types: List[DataType]

    def __post_init__(self):
        if len(self.data_types) > 1:
            raise ValueError("Multiple data types found in name resolution.")
        if len(self.rule_calls) != 1:
            raise ValueError("Multiple or None rule calls found in name resolution.")

    def __str__(self):
        return str(self.rule_calls[0])
