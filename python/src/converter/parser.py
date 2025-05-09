from pathlib import Path
from lark import Lark
from rich import print


def parse():
    this_file = Path(__file__)
    meta_grammar_file = this_file.parent / "lark" / "meta.lark"
    kerml_expressions_file = this_file.parent / "xtext" / "KerMLExpressions.xtext"
    sysml_file = this_file.parent / "xtext" / "SysML.xtext"

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

    print("Parser loaded successfully.")
