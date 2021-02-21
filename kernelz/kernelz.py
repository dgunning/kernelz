from typing import List

import typer
from rich.console import Console
from rich.table import Table

from jupyter import list_kernels, list_kernels_like, get_kernel, Kernel

app = typer.Typer()


def to_table(kernels: List[Kernel]):
    table = Table(show_header=True, header_style="bold green")
    table.add_column('', style='dim')
    table.add_column('Display Name', style='bold')
    table.add_column('Name')
    table.add_column('Created')
    table.add_column('Modified')
    table.add_column('Language')

    row_num = 1
    for kernel in kernels:
        table.add_row(str(row_num),
                      kernel.get_display_name(),
                      kernel.name,
                      kernel.get_date_created().to_formatted_date_string(),
                      kernel.get_date_modified().to_formatted_date_string(),
                      kernel.get_language())
        row_num += 1
    return table


def to_markdown(kernel: Kernel):
    created = kernel.get_date_created().to_formatted_date_string()
    modified = kernel.get_date_modified().to_formatted_date_string()
    template = (
        f"""
    [bold]{kernel.get_display_name()}[/bold] ({kernel.name})
    -------------------------------------------------------------
    [bold]Created[/bold]: [blue]{created}[/blue] [bold]Modified[/bold]: [blue]{modified}[/blue] [bold]Language[/bold]: {kernel.get_language()}
    """
    )
    return template


@app.command()
def show(kernel_name: str):
    """
    Show details about a kernel
    :param kernel_name:
    :return:
    """
    console = Console()

    if kernel_name.isdigit():
        kernel_number = int(kernel_name)
        kernels = list_kernels()
        if kernel_number < 1 or kernel_number > len(kernels):
            console.print(f'No such kernel {kernel_number} .. available kernels are')
            console.print(to_table(kernels))
            return
        else:
            kernel = kernels[kernel_number -1]
    else:
        kernel = get_kernel(kernel_name)
    if kernel:
        console.print(to_markdown(kernel))
    else:
        similar_kernels = list_kernels_like(kernel_name)
        if len(similar_kernels) > 0:
            console.print(f'No kernel named [bold red]{kernel_name}[/bold red] .. do you mean one of the following ...?')
            for kernel in similar_kernels:
                console.print(to_markdown(kernel))
                console.print()
        else:
            console.print(f'\nNo kernel named [bold red]{kernel_name}[/bold red]. Here are the kernels on your system')
            console.print(to_table(list_kernels()))


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
