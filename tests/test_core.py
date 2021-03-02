from kernelz.core import get_environment


def test_get_environment():
    print()
    env = get_environment()
    assert env
    print(env)
