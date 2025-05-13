import typer
from .parser import validate_rules, parse as fparse
from pathlib import Path

app = typer.Typer()


@app.command()
def parse():
    """
    Attempt to parse the KerML and SysML files using the Lark parser.
    """

    validate_rules(fparse())


@app.command()
def convert(output: Path = typer.Argument(..., help="Output file path")):
    if not output.exists():
        output.parent.mkdir(parents=True, exist_ok=True)
    rules = validate_rules(fparse())
    print(f"Found {len(rules)} rules.")
    if rules is None:
        raise typer.Exit(code=1)
    file_content = ""
    start_rule = rules[0]
    file_content += f"start: {start_rule.name} \n\n"
    for rule in rules:
        file_content += f"{rule.name}: {str(rule.body)} \n\n"
    with open(output, "w") as f:
        f.write(file_content)


@app.command()
def test(grammar: Path = typer.Argument(..., help="Converted grammar file path")):
    """
    Test the conversion process by trying to load converted grammar into Lark.
    """
    grammar_content = None
    with open(grammar, "r") as f:
        grammar_content = f.read()

    from lark import Lark

    parser = Lark(grammar_content)


if __name__ == "__main__":
    app()
