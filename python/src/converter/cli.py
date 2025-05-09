import typer
from pathlib import Path
from rich import print

app = typer.Typer()


@app.command()
def try_load():
    """
    Convert a file from one format to another.
    """
    from lark import Lark

    this_file = Path(__file__)
    meta_grammar_file = this_file.parent / "lark" / "meta.lark"
    xtext_file = this_file.parent / "xtext" / "KerMLExpressions.xtext"
    # xtext_file = this_file.parent / "xtext" / "test.xtext"
    parser = None
    with open(meta_grammar_file, "r") as f:
        parser = Lark(f)
        #    parser="lalr")

    xtext_content = None
    with open(xtext_file, "r") as f:
        xtext_content = f.read()

    tree = parser.parse(xtext_content)

    print("Parser loaded successfully.")
    print(tree.pretty())


if __name__ == "__main__":
    app()
