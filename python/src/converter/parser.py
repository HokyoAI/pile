from pathlib import Path
from lark import Lark
from rich import print
from .visitor import XTextVisitor, XTextRuleVisitor


def parse():
    this_file = Path(__file__)
    meta_grammar_file = this_file.parent / "lark" / "meta.lark"

    parser = None
    with open(meta_grammar_file, "r") as f:
        parser = Lark(f)  # lalr parser not working, stick with the slow version

    kerml_expressions_file = this_file.parent / "xtext" / "KerMLExpressions.xtext"
    sysml_file = this_file.parent / "xtext" / "SysML.xtext"

    kerml_expressions_content = None
    with open(kerml_expressions_file, "r") as f:
        kerml_expressions_content = f.read()

    sysml_content = None
    with open(sysml_file, "r") as f:
        sysml_content = f.read()

    kerml_tree = parser.parse(kerml_expressions_content)
    sysml_tree = parser.parse(sysml_content)

    visitor = XTextVisitor()
    visitor.visit_topdown(sysml_tree)
    visitor.visit_topdown(kerml_tree)

    # test_file = this_file.parent / "xtext" / "test.xtext"
    # test_2_file = this_file.parent / "xtext" / "test2.xtext"

    # test_content = None
    # with open(test_file, "r") as f:
    #     test_content = f.read()

    # test_2_content = None
    # with open(test_2_file, "r") as f:
    #     test_2_content = f.read()

    # test_tree = parser.parse(test_content)
    # test_2_tree = parser.parse(test_2_content)

    # visitor = XTextVisitor()
    # visitor.visit_topdown(test_tree)
    # visitor.visit_topdown(test_2_tree)

    if len(visitor.rules) == 0:
        print("No rules found in the XText file.")
        return

    start_rule = None
    for idx, rule in enumerate(visitor.rules):
        rule_visitor = XTextRuleVisitor()
        rule_visitor.visit_topdown(rule)
        if idx == 0:
            start_rule = rule_visitor.rule

    print(str(start_rule.body))
