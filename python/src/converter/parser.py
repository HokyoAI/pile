from pathlib import Path
from lark import Lark


def parse():
    this_file = Path(__file__)
    meta_grammar_file = this_file.parent / "lark" / "meta.lark"
    kerml_expressions_file = this_file.parent / "xtext" / "KerMLExpressions.xtext"
    sysml_file = this_file.parent / "xtext" / "SysML.xtext"
    test_file = this_file.parent / "xtext" / "test.xtext"
    test_2_file = this_file.parent / "xtext" / "test2.xtext"

    parser = None
    with open(meta_grammar_file, "r") as f:
        parser = Lark(f)  # lalr parser not working, stick with the slow version

    kerml_expressions_content = None
    with open(kerml_expressions_file, "r") as f:
        kerml_expressions_content = f.read()

    sysml_content = None
    with open(sysml_file, "r") as f:
        sysml_content = f.read()

    kerml_tree = parser.parse(kerml_expressions_content)
    sysml_tree = parser.parse(sysml_content)

    print("done")
    # test_content = None
    # with open(test_file, "r") as f:
    #     test_content = f.read()
    # test_tree = parser.parse(test_content)
    # visitor = XTextVisitor()
    # visitor.visit_topdown(test_tree)

    # test_2_content = None
    # with open(test_2_file, "r") as f:
    #     test_2_content = f.read()
    # test_2_tree = parser.parse(test_2_content)
    # visitor.visit_topdown(test_2_tree)

    # start_rule = visitor.rules[0]

    # rule_visitor = XTextRuleVisitor()
    # rule_visitor.visit_topdown(start_rule)
    # print(rule_visitor.rule)
