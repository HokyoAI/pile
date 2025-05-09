import typer

app = typer.Typer()


@app.command()
def parse():
    """
    Attempt to parse the KerML and SysML files using the Lark parser.
    """
    from .parser import parse as fparse

    fparse()


if __name__ == "__main__":
    app()
