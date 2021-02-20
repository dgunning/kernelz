from typing import List

import typer
from rich.table import Table
from rich.console import Console

from jupyter import list_kernels, get_kernel, Kernel

app = typer.Typer()


def to_table(kernels: List[Kernel]):
    table = Table(show_header=True, header_style="bold blue")
    table.add_column('', style='dim')
    table.add_column('Display Name')
    table.add_column('Name')
    table.add_column('Created')
    table.add_column('Modified')
    table.add_column('Language')

    rownum = 1
    for kernel in kernels:
        table.add_row(str(rownum),
                      kernel.get_display_name(),
                      kernel.name,
                      kernel.get_date_created().to_formatted_date_string(),
                      kernel.get_date_modified().to_formatted_date_string(),
                      kernel.get_language())
        rownum += 1
    return table


@app.command()
def show(kernel_name: str):
    """
    Show details about a kernel
    :param kernel_name:
    :return:
    """
    kernel = get_kernel(kernel_name)
    typer.echo(kernel)


@app.command(name="list")
def show_all():
    """
    List the available IPython kernels on this machine
    """
    kernels = list_kernels()
    console = Console()
    table = to_table(kernels)

    typer.secho("\nConda Kernels\n", fg=typer.colors.BRIGHT_BLUE)
    console.print(table)


if __name__ == '__main__':
    app()
