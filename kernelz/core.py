import subprocess


def run_command(*command) -> str:
    """
    Run the command and return the result as a string
    :param command: The command to run
    :return: The result of the command as a string
    """
    return subprocess.run(command,
                          stdout=subprocess.PIPE).stdout.decode().strip()
