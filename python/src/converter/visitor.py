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
)


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
        visitor = ReturnTypeVisitor()
        visitor.visit_topdown(tree)
        self.rule.return_type = visitor.names

    def rule_body(self, tree: Tree):
        """
        Will enter on the rule body for the rule statement.
        """
        transformer: Transformer = RuleBodyTransformer(visit_tokens=True)
        self.rule.body = transformer.transform(tree)


class ReturnTypeVisitor(Visitor):
    """
    Visit a single rule in the XText Tree
    """

    def __init__(self):
        super().__init__()
        self.names = []

    def name(self, tree: Tree):
        token: Token = tree.children[0]
        self.names.append(token.value)


@v_args(inline=True)
class RuleBodyTransformer(Transformer):
    """Transforms Lark parse trees into dataclass objects."""

    def rule_body(self, passthru):
        # The rule body is the main entry point for the transformation
        return passthru

    def statements(self, alternative):
        return alternative

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

    def item(self, passthru):
        return passthru

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

    def cardinality(self, cardinality):
        # Convert the cardinality symbol to enum
        return cardinality

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

    # def predicate(self, *args):
    #     # Handle predicates
    #     # The first argument is the arrow, second is the expression
    #     return GroupExpression(expression=args[1], negated=False, cardinality_type=None)

    def basic_element(self, passthru):
        return passthru

    def pure_parsing(self, passthru):
        return passthru

    def literal(self, lit: Token):
        # Process literals
        return LiteralExpression(lit.value)

    # Handle other terminal types
    def terminal_rules(self, passthru):
        return passthru

    def char_range(self, start, end):
        return RegularExpression((f"{start}-{end}"))

    def wildcard(self, prefix, suffix):
        return RegularExpression((f"{prefix}.{suffix}"))

    def until(self, start, end):
        return RegularExpression((f"{start}.*{end}"))

    # # Handle assignment structures
    # def assignment_item(self, item):
    #     # Just pass through the assignment item
    #     return item

    # def property_assignment(self, *args):
    #     # Create an atomic expression for property assignments
    #     # Simplified representation
    #     return AtomicExpression(value=f"property_assignment:{args}")

    # def list_prop_assignment(self, *args):
    #     # Create an atomic expression for list property assignments
    #     return AtomicExpression(value=f"list_prop_assignment:{args}")

    # def bool_prop_assignment(self, *args):
    #     # Create an atomic expression for boolean property assignments
    #     return AtomicExpression(value=f"bool_prop_assignment:{args}")

    # def non_parsing_assignment(self, item):
    #     # Pass through non-parsing assignments
    #     return item

    # def non_parsing_type(self, data_type):
    #     return AtomicExpression(value=f"non_parsing_type:{data_type}")

    # def non_parsing_equals(self, *args):
    #     return AtomicExpression(value=f"non_parsing_equals:{args}")

    # def non_parsing_list(self, *args):
    #     return AtomicExpression(value=f"non_parsing_list:{args}")

    # # Handle name resolutions and other complex structures
    # def left_sides(self, *args):
    #     return args

    # def right_sides(self, value):
    #     return value

    # def name_resolution(self, *names):
    #     return f"name_resolution:{names}"

    # def XTEXT_CURRENT(self, _):
    #     return "current"


# class StatementsTransformer(Transformer):
#     # def statements(self, items):
#     #     # A statement is just an alternative
#     #     return Statement(items[0])

#     # def alternative(self, items):
#     #     alt = Alternative()
#     #     for item in items:
#     #         if isinstance(item, Sequence):
#     #             alt.add_sequence(item)
#     #         else:
#     #             # This handles the case where we might have just one item
#     #             # that's not already wrapped in a Sequence
#     #             seq = Sequence([item])
#     #             alt.add_sequence(seq)
#     #     return alt

#     # def sequence(self, items):
#     #     seq = Sequence()
#     #     for item in items:
#     #         seq.add_element(item)
#     #     return seq

#     def literal(self, n):
#         (n,) = n
#         return str(n)

#     def rule_call(self, n):
#         (n,) = n
#         token: Token = n.children[0]
#         return str(token.value)

#     def basic_element(self, n):
#         return passthrough(n)

#     def terminal_rules(self, n):
#         return passthrough(n)

#     def pure_parsing(self, n):
#         return passthrough(n)

#     def char_range(self, items):
#         return RegExp(f"{items[0]}-{items[1]}")

#     def wildcard(self, items):
#         return RegExp(f"{items[0]}.{items[1]}")

#     def until(self, items):
#         return RegExp(f"{items[0]}.*{items[1]}")
