import difflib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import pendulum

from kernelz.core import run_command

__all__ = ['list_kernels', 'list_kernel_dirs', 'list_kernels_like', 'list_conda_envs',
           'get_kernel', 'Kernel', 'CondaEnv']

env = os.environ


@dataclass
class Kernel:
    name: str
    kernel_json: Dict[str, str]
    stat: os.stat_result

    def get_name(self):
        return self.name

    def get_display_name(self):
        return self.kernel_json.get('display_name')

    def get_language(self):
        return self.kernel_json.get('language')

    def get_date_created(self):
        return pendulum.from_timestamp(self.stat.st_ctime)

    def get_date_modified(self):
        return pendulum.from_timestamp(self.stat.st_mtime)

    def get_executable(self):
        return self.kernel_json.get('argv')[0]

    def get_argv(self):
        return self.kernel_json.get('argv')

    def __repr__(self):
        created = self.get_date_created().to_formatted_date_string()
        modified = self.get_date_modified().to_formatted_date_string()
        return f"""
        Display Name: {self.name}
        Created: {created} Modified: {modified} Language: {self.get_language()}
        """


def _last_modified(path: Path):
    path.stat()


_temp_dirs = {}


def _make_temp_once(name):
    """Make or reuse a temporary directory.
    If this is called with the same name in the same process, it will return
    the same directory.
    """
    try:
        return _temp_dirs[name]
    except KeyError:
        d = _temp_dirs[name] = tempfile.mkdtemp(prefix=name + '-')
        return d


def get_home_dir():
    """Get the user home directory"""
    return os.path.realpath(os.path.expanduser('~'))


def jupyter_config_dir():
    """
    Returns JUPYTER_CONFIG_DIR if defined, else ~/.jupyter
    """
    if env.get('JUPYTER_NO_CONFIG'):
        return _make_temp_once('jupyter-clean-cfg')
    elif env.get('JUPYTER_CONFIG_DIR'):
        return env['JUPYTER_CONFIG_DIR']
    else:
        home_dir = get_home_dir()
        return os.path.join(home_dir, '.jupyter')


ENV_JUPYTER_PATH = [os.path.join(sys.prefix, 'share', 'jupyter')]


def envset(name):
    """Return True if the given environment variable is set
    An environment variable is considered set if it is assigned to a value
    other than 'no', 'n', 'false', 'off', '0', or '0.0' (case insensitive)
    """
    return os.environ.get(name, 'no').lower() not in ['no', 'n',
                                                      'false', 'off',
                                                      '0', '0.0']


def jupyter_data_dir():
    """Get the config directory for Jupyter data files for this platform and user.
    These are non-transient, non-configuration files.
    Returns JUPYTER_DATA_DIR if defined, else a platform-appropriate path.
    """

    if env.get('JUPYTER_DATA_DIR'):
        return env['JUPYTER_DATA_DIR']

    home = get_home_dir()

    if sys.platform == 'darwin':
        return os.path.join(home, 'Library', 'Jupyter')
    elif os.name == 'nt':
        appdata = os.environ.get('APPDATA', None)
        if appdata:
            return os.path.join(appdata, 'jupyter')
        else:
            return os.path.join(jupyter_config_dir(), 'data')
    else:
        # Linux, non-OS X Unix, AIX, etc.
        xdg = env.get("XDG_DATA_HOME", None)
        if not xdg:
            xdg = os.path.join(home, '.local', 'share')
        return os.path.join(xdg, 'jupyter')


def _get_system_jupyter_path():
    if os.name == 'nt':
        programdata = os.environ.get('PROGRAMDATA', None)
        if programdata:
            return [os.path.join(programdata, 'jupyter')]
        else:
            return [os.path.join(sys.prefix, 'share', 'jupyter')]
    else:
        return ["/usr/local/share/jupyter", "/usr/share/jupyter"]


def jupyter_path(*subdirs):
    """Return a list of directories to search for data files
    JUPYTER_PATH environment variable has highest priority.
    If the JUPYTER_PREFER_ENV_PATH environment variable is set,
    the environment-level
    directories will have priority over user-level directories.
    If ``*subdirs`` are given, that subdirectory will be added to each element.
    Examples:
    >>> jupyter_path()
    ['~/.local/jupyter', '/usr/local/share/jupyter']
    >>> jupyter_path('kernels')
    ['~/.local/jupyter/kernels', '/usr/local/share/jupyter/kernels']
    """

    # First check the JUPYTER_PATH environment variable
    paths = [p.rstrip(os.sep)
             for p in os.environ.get('JUPYTER_PATH', '').split(os.pathsep)
             if os.environ.get('JUPYTER_PATH')]

    # Next check the user's data dir
    user_dir = jupyter_data_dir()
    env_jupyter_path = [os.path.join(sys.prefix, 'share', 'jupyter')]
    system_jupyter_path = _get_system_jupyter_path()
    env_path = [p for p in env_jupyter_path if p not in system_jupyter_path]
    if envset('JUPYTER_PREFER_ENV_PATH'):
        paths.extend(env_path)
        paths.append(user_dir)
    else:
        paths.append(user_dir)
        paths.extend(env_path)

    paths.extend(system_jupyter_path)

    # add subdir, if requested
    if subdirs:
        paths = [os.path.join(p, *subdirs) for p in paths]
    return paths


def list_kernel_dirs():
    """
    :return: a list of the kernels on this machine
    """
    return [kernel_dir
            for kernel_path in filter(os.path.exists, jupyter_path('kernels'))
            for kernel_dir in Path(kernel_path).iterdir()
            if kernel_dir.is_dir()]


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


def list_kernels_like(kernel_search_term: str):
    kernels = list_kernels()
    kernel_matches = difflib.get_close_matches(kernel_search_term,
                                               [k.name for k in kernels])
    similar_named_kernels = list(filter(lambda k: k.name in kernel_matches,
                                        kernels))
    return similar_named_kernels


def get_kernel(kernel_name: str) -> Optional[Kernel]:
    """
    Get a kernel with the given name
    :param kernel_name: The kernel name
    :return: the kernel with the name
    """
    kernels = list_kernels(kernel_name)
    if len(kernels) == 1:
        return kernels[0]


@dataclass
class CondaEnv:
    name: str
    path: str
    active: bool


def list_conda_envs():
    result = run_command('conda', 'env', 'list')
    envs = []
    for line in result.splitlines():
        if 'conda environments' in line:
            continue
        parts = re.sub(' +', ' ', line).split(' ')
        if len(parts) < 2:
            continue
        if len(parts) == 2:
            name, path = parts
            is_active = False
        elif len(parts) == 3:
            name, is_active, path = parts[0], parts[1] == '*', parts[2]
        if not name:
            name = os.path.basename(path)
        envs.append(CondaEnv(name, path, is_active))

    return envs
