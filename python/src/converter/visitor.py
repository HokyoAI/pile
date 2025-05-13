from lark import Visitor, Tree, Token, Transformer, v_args
from .rule import XTextRule
from .expression import (
    SequenceExpression,
    OrExpression,
    CardinalityType,
    LiteralExpression,
    RegularExpression,
    RuleCallExpression,
    GroupExpression,
    DataType,
    NameResolution,
)
from .utils import XTEXT_CURRENT, NON_PARSING


class XTextVisitor(Visitor):
    """
    TODO: Handle grammar and import statements. Only handle rule statements for now.
    """

    def __init__(self):
        super().__init__()
        self.rules: list[Tree] = []

    def rule_statement(self, tree: Tree):
        """
        Will collect all the rule statements made in the xtext tree.
        """
        self.rules.append(tree)


class XTextRuleVisitor(Visitor):
    """
    Visit a single rule in the XText Tree
    """

    def __init__(self):
        super().__init__()
        self.rule: XTextRule = XTextRule()

    def override_dec(self, tree: Tree):
        self.rule.is_override = True

    def final_dec(self, tree: Tree):
        self.rule.is_final = True

    def deprecated_dec(self, tree: Tree):
        self.rule.is_deprecated = True

    def exported_dec(self, tree: Tree):
        self.rule.is_exported = True

    def terminal_mod(self, tree: Tree):
        self.rule.is_terminal = True

    def enum_mod(self, tree: Tree):
        self.rule.is_enum = True

    def fragment_mod(self, tree: Tree):
        self.rule.is_fragment = True

    def rule_name(self, tree: Tree):
        rule_name_token: Token = tree.children[0].children[0]
        self.rule.name = rule_name_token.value

    def return_type(self, tree: Tree):
        transformer: Transformer = ReturnTypeTransformer()
        self.rule.return_type = transformer.transform(tree)

    def rule_body(self, tree: Tree):
        """
        Will enter on the rule body for the rule statement.
        """
        transformer: Transformer = RuleBodyTransformer(visit_tokens=True)
        self.rule.body = transformer.transform(tree)


@v_args(inline=True)
class ReturnTypeTransformer(Transformer):
    """
    Visit a single rule in the XText Tree
    """

    def __init__(self):
        super().__init__()
        self.names = []

    def name(self, *args):
        token: Token = args[0]
        return token.value

    def qualified_name(self, *args):
        qname = [str(arg) for arg in args]
        return qname

    def data_type(self, *args):
        dtype = DataType(namespace=args[0], qualified_name=args[1])
        return dtype

    def return_type(self, *args):
        # If there's only one name, return it directly
        return args[0]


@v_args(inline=True)
class RuleBodyTransformer(Transformer):
    """Transforms Lark parse trees into dataclass objects."""

    def passthru(self, passthru):
        # Just pass through the item
        return passthru

    type_spec = passthru
    assignment_item = passthru
    non_parsing_assignment = passthru
    right_sides = passthru
    terminal_rules = passthru
    pure_parsing = passthru
    basic_element = passthru
    cardinality = passthru
    item = passthru
    statements = passthru
    rule_body = passthru

    def alternative(self, *args):
        # If there's only one sequence, return it directly
        if len(args) == 1:
            return args[0]
        # Otherwise, create an OrExpression
        return OrExpression(expressions=list(args))

    def sequence(self, *args):
        # If there's only one item, return it directly
        if len(args) == 1:
            return args[0]
        # Otherwise, create a SequenceExpression
        expr = SequenceExpression(expressions=list(args))
        return expr

    def rule_call(self, name):
        # Return the name of the rule being called
        return RuleCallExpression(name)

    def group(self, *args):
        if len(args) == 1:
            return args[0]  # Return the single expression
        negated = False
        cardinality_type = None
        expression = None
        for arg in args:
            if isinstance(arg, bool):
                negated = arg
            elif isinstance(arg, CardinalityType):
                cardinality_type = arg
            else:
                expression = arg
        expr = GroupExpression(
            negated=negated, expression=expression, cardinality_type=cardinality_type
        )
        return expr

    def optional(self):
        # Optional cardinality
        return CardinalityType.OPTIONAL

    def at_least_one(self):
        # At least one cardinality
        return CardinalityType.AT_LEAST_ONE

    def zero_or_more(self):
        # Zero or more cardinality
        return CardinalityType.ZERO_OR_MORE

    def negation(self):
        # Return True to indicate negation
        return True

    def predicate(self, *args):
        # Handle predicates
        # The first argument is the arrow, second is the expression
        return args[0]

    def literal(self, lit: Token):
        # Process literals
        return LiteralExpression(lit.value)

    def char_range(self, start, end):
        return RegularExpression((f"{start}-{end}"))

    def wildcard(self, prefix, suffix):
        return RegularExpression((f"{prefix}.{suffix}"))

    def until(self, start, end):
        return RegularExpression((f"{start}.*{end}"))

    def name(self, *args):
        token: Token = args[0]
        return token.value

    def qualified_name(self, *args):
        qname = [str(arg) for arg in args]
        return qname

    def data_type(self, *args):
        dtype = DataType(namespace=args[0], qualified_name=args[1])
        return dtype

    def name_resolution(self, *names):
        data_types = []
        rule_calls = []
        for name in names:
            if isinstance(name, DataType):
                data_types.append(name)
            elif isinstance(name, RuleCallExpression):
                rule_calls.append(name)
            else:
                raise ValueError(f"Unknown name resolution type: {name}")

        return NameResolution(rule_calls=rule_calls, data_types=data_types)

    def xtext_current(self, *args):
        return XTEXT_CURRENT

    def property_assignment(self, *args):
        # Create an atomic expression for property assignments
        # Simplified representation
        return args[1]  # return right side of assignment

    def list_prop_assignment(self, *args):
        # Create an atomic expression for list property assignments
        return args[1]  # return right side of assignment

    def bool_prop_assignment(self, *args):
        # Create an atomic expression for boolean property assignments
        return args[1]  # return right side of assignment

    def non_parsing_type(self, data_type):
        return NON_PARSING

    def non_parsing_equals(self, *args):
        return NON_PARSING

    def non_parsing_list(self, *args):
        return NON_PARSING
