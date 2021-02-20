import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List

import pendulum
from jupyter_core.paths import jupyter_path

__all__ = ['list_kernels', 'list_kernel_dirs', 'get_kernel', 'Kernel']


@dataclass
class Kernel:
    name: str
    kernel_json: Dict[str, str]
    stat: os.stat_result

    def get_display_name(self):
        return self.kernel_json.get('display_name')

    def get_language(self):
        return self.kernel_json.get('language')

    def get_date_created(self):
        return pendulum.from_timestamp(self.stat.st_ctime)

    def get_date_modified(self):
        return pendulum.from_timestamp(self.stat.st_mtime)


def run_command(*command) -> str:
    """
    Run the command and return the result as a string
    :param command: The command to run
    :return: The result of the command as a string
    """
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode().strip()


def _last_modified(path: Path):
    path.stat()


def list_kernel_dirs():
    """
    :return: a list of the kernels on this machine
    """
    return [kernel_dir
            for kernel_path in filter(os.path.exists, jupyter_path('kernels'))
            for kernel_dir in Path(kernel_path).iterdir() if kernel_dir.is_dir()]


def list_kernels(*kernel_names):
    """List the jupyter kernels on this machine"""
    kernel_dirs = list_kernel_dirs()
    kernels = []
    for kernel_dir in kernel_dirs:
        if kernel_names and kernel_dir.name not in kernel_names:
            continue
        kernel_file: Path = kernel_dir / 'kernel.json'
        if kernel_file.exists():
            with kernel_file.open('r') as f:
                kernel_json = json.load(f)
                kernels.append(Kernel(name=kernel_dir.name,
                                      kernel_json=kernel_json,
                                      stat=kernel_file.stat()))
    return kernels


def get_kernel(kernel_name: str) -> Optional[Kernel]:
    """
    Get a kernel with the given name
    :param kernel_name: The kernel name
    :return: the kernel with the name
    """
    kernels = list_kernels(kernel_name)
    if len(kernels) == 1:
        return kernels[0]

