from nox_poetry import session


def install(session, *dependencies):
    for dep in dependencies:
        session.install(dep)


@session(python=["3.7", "3.8", "3.9"])
def tests(session):
    install(session, 'pytest', 'jupyter', 'pendulum')
    session.run('pytest')
