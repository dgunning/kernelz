import subprocess
import sys
import os
from dataclasses import dataclass

__all__ = ['run_command', 'get_environment', 'get_virtual_environment', 'Environment']


def run_command(*command) -> str:
    """
    Run the command and return the result as a string
    :param command: The command to run
    :return: The result of the command as a string
    """
    return subprocess.run(command,
                          stdout=subprocess.PIPE).stdout.decode().strip()


def get_python():
    return sys.executable


def get_virtual_environment():
    """
    Get the virtual env if any that the code is running in
    :return:
    """
    virtual_env = os.environ.get('VIRTUAL_ENV')
    if virtual_env:
        return virtual_env, 'virtualenv'
    else:
        conda_env = os.environ.get['CONDA_DEFAULT_ENV']
        if conda_env:
            return conda_env, 'conda'


@dataclass
class Environment:

    executable: str
    virtual_env: str


def get_environment():
    virtual_env = get_virtual_environment()
    return Environment(sys.executable, virtual_env)
