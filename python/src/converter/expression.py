from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class CardinalityType(Enum):
    OPTIONAL = "?"
    AT_LEAST_ONE = "+"
    ZERO_OR_MORE = "*"


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
        result = f"{'!' if self.negated else ''}({self.expression})"
        if self.cardinality_type is not None:
            result += f" {self.cardinality_type.value}"
        return result
