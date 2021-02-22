import tempfile
import nox

nox.options.sessions = "safety", "tests"
from nox_poetry import session


def install(session, *dependencies):
    for dep in dependencies:
        session.install(dep)


@session(python=["3.7", "3.8", "3.9"])
def tests(session):
    install(session, 'pytest', 'jupyter', 'pendulum')
    session.run('pytest')


@session(python="3.7")
def safety(session):
    session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output=requirements.txt",
            external=True,
        )
    session.install("jupyter")
    session.run("safety", "check", f"--file=requirements.txt", "--full-report")
