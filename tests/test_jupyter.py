import os

from kernelz.jupyter import list_kernels, list_kernel_dirs, get_kernel, list_kernels_like


def setenv(monkeypatch):
    monkeypatch.setenv('JUPYTER_PATH', 'tests/data')


def test_list_kernel_dirs(monkeypatch):
    setenv(monkeypatch)
    kernel_dirs = list_kernel_dirs()
    print(kernel_dirs)
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