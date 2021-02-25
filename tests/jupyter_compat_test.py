import pytest

from kernelz.jupyter import jupyter_path


@pytest.mark.skip(reason="Test only with jupyter path installed")
def _test_jupyter_path():
    import jupyter_core.paths
    assert jupyter_core.paths.jupyter_path('kernels') == jupyter_path('kernels')
