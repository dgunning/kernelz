import os

from kernelz.jupyter import list_kernels, list_kernel_dirs, get_kernel, list_kernels_like
from kernelz.kernelz import find_kernel


def setenv(monkeypatch):
    monkeypatch.setenv('JUPYTER_PATH', 'tests/data')


def test_list_kernel_dirs(monkeypatch):
    setenv(monkeypatch)
    kernel_dirs = list_kernel_dirs()
    assert f'tests{os.sep}data{os.sep}kernels{os.sep}squad' in list(map(str, kernel_dirs))


def test_list_kernels(monkeypatch):
    setenv(monkeypatch)
    kernel_names = [k.name for k in list_kernels()]
    assert 'squad' in kernel_names


def test_list_kernels_like(monkeypatch):
    setenv(monkeypatch)
    kernels = list_kernels_like('card')
    assert 'cord' in [kernel.name for kernel in kernels]


def test_list_kernels_by_name(monkeypatch):
    setenv(monkeypatch)
    kernels = list_kernels('squad')
    assert kernels[0].name == 'squad' == kernels[-1].name


def test_get_kernel(monkeypatch):
    setenv(monkeypatch)
    kernel = get_kernel('squad')
    assert kernel


def test_get_argv(monkeypatch):
    setenv(monkeypatch)
    kernel = get_kernel('squad')
    assert kernel.get_argv()
    assert type(kernel.get_argv()) == list
    assert 'python' in kernel.get_argv()[0]


def test_get_executable(monkeypatch):
    setenv(monkeypatch)
    kernel = get_kernel('squad')
    assert 'python' in kernel.get_executable()


def test_find_kernel(monkeypatch):
    setenv(monkeypatch)
    kernel = find_kernel('squad')
    assert kernel
    assert kernel.name == 'squad'
