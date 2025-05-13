import typer
from .parser import process_rules, parse as fparse
from pathlib import Path

app = typer.Typer()


@app.command()
def parse():
    """
    Attempt to parse the KerML and SysML files using the Lark parser.
    """

    process_rules(fparse())


@app.command()
def convert(output: Path = typer.Argument(..., help="Output file path")):
    if not output.exists():
        output.parent.mkdir(parents=True, exist_ok=True)
    rules = process_rules(fparse())
    if rules is None or len(rules) == 0:
        print("No rules found.")
        raise typer.Exit(code=1)

    print(f"Found {len(rules)} rules.")

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

    test_directory = Path(__file__).parent.parent.parent / "tests"

    test_files = list(test_directory.glob("*.sysml"))

    for test_file in test_files:
        print(f"Testing {test_file.name}...")
        with open(test_file, "r") as f:
            test_content = f.read()
            try:
                parser.parse(test_content)
                print(f"Test passed for {test_file.name}")
            except Exception as e:
                print(f"Test failed for {test_file.name}: {e}")


if __name__ == "__main__":
    app()
