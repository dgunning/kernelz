import os
from typing import List

import typer
from rich.console import Console
from rich.table import Table

from kernelz.core import run_command
from kernelz.jupyter import list_kernels, list_kernels_like, get_kernel, Kernel, CondaEnv, list_conda_envs

"""
Kernelz

"""

__all__ = ['kernels_to_table', 'to_markdown']

app = typer.Typer()


def kernels_to_table(kernels: List[Kernel]) -> Table:
    """
    Renders the kernel list to a table
    :param kernels:
    :return: a Table
    """
    table = Table(show_header=True, header_style="bold blue")
    table.add_column('', style='dim')
    table.add_column('Name', style='bold')
    table.add_column('Created')
    table.add_column('Modified')
    table.add_column('Language')
    table.add_column('Valid')

    row_num = 1
    for kernel in kernels:
        table.add_row(str(row_num),
                      kernel.name,
                      kernel.get_date_created().to_formatted_date_string(),
                      kernel.get_date_modified().to_formatted_date_string(),
                      kernel.get_language(),
                      'Valid' if os.path.exists(kernel.get_executable())
                      else 'Invalid')
        row_num += 1
    return table


def envs_to_table(envs: List[CondaEnv]) -> Table:
    table = Table(show_header=True, header_style="bold blue")
    table.add_column('', style='dim')
    table.add_column('Name', style='bold')
    table.add_column('Path')
    row_num = 1
    for env in envs:
        table.add_row((str(row_num)),
                      env.name,
                      env.path)
        row_num += 1
    return table


def to_markdown(kernel: Kernel):
    """
    Renders to a text representation of the kernel
    :param kernel:
    :return:
    """
    created = kernel.get_date_created().to_formatted_date_string()
    modified = kernel.get_date_modified().to_formatted_date_string()
    template = (
            f"""
 [bold]{kernel.get_name()}[/bold]
 [green]{kernel.get_executable()}[/green]
 -------------------------------------------------------------\n""" +
            f" [bold]Created[/bold]: [blue]{created}[/blue]  "
            f" [bold]Modified[/bold]: [blue]{modified}[/blue] [bold] " +
            f" Language[/bold]: {kernel.get_language()}" +
            "\n"
    )
    return template


def warn(*messages):
    console = Console()
    console.print(*messages)


def find_kernel(kernel_name: str):
    """
    Find the kernel with that name or number
    :param kernel_name: The name of the kernel or the number of the kernel
                        in the list
    :return: the kernel
    """
    if kernel_name.isdigit():
        kernel_number = int(kernel_name)
        kernels = list_kernels()
        if kernel_number > 0 or kernel_number <= len(kernels):
            kernel = kernels[kernel_number + 1]
    else:
        kernel = get_kernel(kernel_name)
    if kernel:
        return kernel


@app.command()
def about():
    """
    Show information about kernelz
    """
    console = Console()
    console.print("""
  [bold]Kernelz - View and manage your conda kernels[/bold]

  Kernelz is a tool for viewing and working with conda kernels
  See https://github.com/dgunning/kernelz for more information. \n
    """)


@app.command()
def run(kernel_name: str):
    """
    Open a python console on the given kernel
    """
    kernel = find_kernel(kernel_name)
    if kernel:
        if os.path.exists(kernel.get_executable()):
            import subprocess
            subprocess.run(kernel.get_executable())
        else:
            warn('Cannot find kernel python', kernel.get_executable())
    else:
        warn('No such kernel', kernel_name)


@app.command()
def show(kernel_name: str):
    """
    Show details about a kernel, using the name or kernel number
    """
    console = Console()
    kernel = find_kernel(kernel_name)
    if kernel:
        console.print(to_markdown(kernel))
    else:
        similar_kernels = list_kernels_like(kernel_name)
        if len(similar_kernels) > 0:
            console.print(
                f'No kernel named [bold red]{kernel_name}[/bold red] ' +
                '.. do you mean one of the following ...?')
            for kernel in similar_kernels:
                console.print(to_markdown(kernel))
                console.print()
        else:
            console.print(
                f'\nNo kernel named [bold red]{kernel_name}[/bold red]. ' +
                'Here are the kernels on your system')
            console.print(kernels_to_table(list_kernels()))
    if kernel:
        return kernel


@app.command()
def view(kernal_name: str):
    """
    Show details about a kernel, using the name or kernel number
    """
    return show(kernal_name)


@app.command()
def freeze(kernel_name: str):
    """
    Show the installed dependencies in this kernel. Uses pip freeze
    :param kernel_name: The kernel name
    """
    kernel = find_kernel(kernel_name)
    if kernel:
        console = Console()
        result = run_command(kernel.get_executable(), '-m', 'pip', 'freeze')
        console.print()
        console.print(f'[bold]# Packages Installed in '
                      f'{kernel.get_display_name()}[/bold]')
        console.print(result)
    else:
        warn('No such kernel', kernel_name)


@app.command(name="list")
def show_all():
    """
    List the available kernels on this machine
    """
    kernels = list_kernels()
    console = Console()
    table = kernels_to_table(kernels)

    typer.secho("\nConda Kernels\n", fg=typer.colors.BRIGHT_BLUE)
    console.print(table)


@app.command()
def envs():
    """
    List the available conda envs on this machine
    """
    conda_envs = list_conda_envs()
    console = Console()
    table = envs_to_table(conda_envs)
    typer.secho("\nConda Environments\n", fg=typer.colors.BRIGHT_BLUE)
    console.print(table)


if __name__ == '__main__':
    app()
