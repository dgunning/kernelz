from kernelz.core import run_command
import typer


def test_show_kernels(monkeypatch):
    result = run_command('kernelz.cmdline')
    typer.echo(result)
