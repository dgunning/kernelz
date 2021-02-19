import typer
from tabulate import tabulate

from jupyter import list_kernels

app = typer.Typer()


@app.command()
def create():
    typer.echo("Creating user: Hiro Hamada")


@app.command()
def show():
    """
    Show the available IPython kernels on this machine
    """
    kernels = list_kernels()
    table = tabulate([[k.get_display_name(),
                       k.name,
                       k.get_date_created().to_formatted_date_string(),
                       k.get_date_modified().to_formatted_date_string(),
                       k.get_language(),
                       ] for k in kernels],
                     headers=['Display Name', 'Name',  'Created', 'Modified', 'Language'])

    typer.secho(f"\nConda Kernels\n", fg=typer.colors.BRIGHT_BLUE)
    typer.echo(table)


if __name__ == '__main__':
    app()
