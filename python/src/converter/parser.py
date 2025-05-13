from pathlib import Path
from lark import Lark
from rich import print
from .visitor import XTextVisitor, XTextRuleVisitor
from .rule import XTextRule


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

    rules: list[XTextRule] = []
    for idx, rule in enumerate(visitor.rules):
        rule_visitor = XTextRuleVisitor()
        rule_visitor.visit_topdown(rule)
        rules.append(rule_visitor.rule)

    return rules


def _remove_overriden_rules(full_ruleset: list[XTextRule], rule: XTextRule):
    """Remove rules that are overridden by the given rule."""
    indexes_to_remove = []
    for idx, existing_rule in enumerate(full_ruleset):
        if existing_rule.name == rule.name:
            indexes_to_remove.append(idx)
    # Remove items in reverse order to avoid index shifting problems
    for idx in sorted(indexes_to_remove, reverse=True):
        full_ruleset.pop(idx)


def validate_rules(rules: list[XTextRule]):
    if len(rules) == 0:
        print("No rules found.")
        return

    full_ruleset: list[XTextRule] = []

    defined_rule_names = set()
    used_rule_names = set()
    transformed_rule_names: dict[str, str] = {}
    overriden_rule_names: set[str] = set()
    finalized_rule_names: set[str] = set()
    for rule in rules:
        if rule.name in finalized_rule_names:
            if rule.is_final:
                raise ValueError(f"Rule '{rule.name}' is marked as final twice")
            else:
                print(f"Warning: Rule '{rule.name}' has already been finalized.")
                continue

        # for overrides, ignore any future rules but don't error
        if rule.name in overriden_rule_names:
            print(f"Warning: Rule '{rule.name}' is overridden.")
            continue

        defined_rule_names.add(rule.name)
        used_rule_names.update(rule.called_rules)

        if rule.is_final:
            finalized_rule_names.add(rule.name)
            _remove_overriden_rules(full_ruleset, rule)

        if rule.is_override:
            overriden_rule_names.add(rule.name)
            _remove_overriden_rules(full_ruleset, rule)

        full_ruleset.append(rule)

    undefined_rule_names = used_rule_names - defined_rule_names
    if undefined_rule_names:
        print("Warning: Some rules are used but not defined.")
        print(f"Undefined Rules: {undefined_rule_names}")
        return

    return full_ruleset


"""
Need to handle the following cases:
empty expressions give us rules like this
empty_feature:

terminal rules, regexs, and enum rules

override and final decorators

hidden section of grammar
"""
