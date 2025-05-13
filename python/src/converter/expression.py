from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from abc import ABC


class CardinalityType(Enum):
    OPTIONAL = "?"
    AT_LEAST_ONE = "+"
    ZERO_OR_MORE = "*"


@dataclass
class DataType:
    namespace: str
    qualified_name: list[str]


class Expression(ABC):
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

    def __str__(self):
        return f"/{self.value}/"


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
        result = f"{'!' if self.negated else ''}({str(self.expression)})"
        if self.cardinality_type is not None:
            result += f"{self.cardinality_type.value}"
        return result


@dataclass
class NameResolution(Expression):
    rule_calls: List[RuleCallExpression]
    data_types: List[DataType]

    def __post_init__(self):
        if len(self.data_types) > 1:
            raise ValueError("Multiple data types found in name resolution.")
        if len(self.rule_calls) != 1:
            raise ValueError("Multiple or None rule calls found in name resolution.")

    def __str__(self):
        return str(self.rule_calls[0])
