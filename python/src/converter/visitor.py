from lark import Visitor, Tree, Token, Transformer
from .rule import XTextRule


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

    def statements(self, tree: Tree):
        """
        Will collect all the statements made in the rule.
        """
        pass
        # print(tree.pretty())
        # transformer = StatementsTransformer()
        # self.rule.statements = transformer.transform(tree)


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


class StatementsTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.statements = []

    def statements(self, items):
        # A statement is just an alternative
        return Statement(items[0])

    def alternative(self, items):
        alt = Alternative()
        for item in items:
            if isinstance(item, Sequence):
                alt.add_sequence(item)
            else:
                # This handles the case where we might have just one item
                # that's not already wrapped in a Sequence
                seq = Sequence([item])
                alt.add_sequence(seq)
        return alt

    def sequence(self, items):
        seq = Sequence()
        for item in items:
            seq.add_element(item)
        return seq
