import nox
from nox_poetry import session

nox.options.sessions = "safety", "tests"


def install(session, *dependencies):
    """
    Install the listed dependencies in the session
    :return:
    """
    for dep in dependencies:
        session.install(dep)


@session(python=["3.7", "3.8", "3.9"])
def tests(session):
    """
    Run the tests
    """
    install(session, 'pytest', 'typer', 'pendulum', 'rich')
    session.run('pytest')


@session(python="3.7")
def safety(session):
    """
    Run safety check
    """
    session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output=requirements.txt",
            external=True,
        )
    session.run("safety", "check", f"--file=requirements.txt", "--full-report")


@session()
def bandit(session):
    """
    Run bandit security check
    """
    session.run("bandit", "kernelz", external=True)


@session()
def flake8(session):
    """
    Run flake8 code inspection
    """
    session.run("flake8", "kernelz", '--max-line-length=127', external=True)
