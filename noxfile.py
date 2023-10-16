from pathlib import Path
from tempfile import TemporaryDirectory

import nox

ROOT = Path(__file__).parent
TESTS = ROOT / "tests"
PYPROJECT = ROOT / "pyproject.toml"


nox.options.sessions = []


def session(default=True, **kwargs):  # noqa: D103
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(**kwargs)(fn)

    return _session


@session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "pypy3"])
def tests(session):
    """
    Run the test suite with a corresponding Python version.
    """
    session.install(ROOT, "-r", TESTS / "requirements.txt")
    if session.posargs == ["coverage"]:
        session.install("coverage[toml]")
        session.run("coverage", "run", "-m", "pytest")
        session.run("coverage", "report")
    else:
        session.run("pytest", *session.posargs, TESTS)


@session(tags=["build"])
def build(session):
    """
    Build a distribution suitable for PyPI and check its validity.
    """
    session.install("build", "twine")
    with TemporaryDirectory() as tmpdir:
        session.run("python", "-m", "build", ROOT, "--outdir", tmpdir)
        session.run("twine", "check", "--strict", tmpdir + "/*")


@session(tags=["style"])
def style(session):
    """
    Check Python code style.
    """
    session.install("ruff")
    session.run("ruff", "check", TESTS, __file__)


@session(default=False)
def requirements(session):
    """
    Update the project's pinned requirements. Commit the result.
    """
    session.install("pip-tools")
    for each in [TESTS / "requirements.in"]:
        session.run(
            "pip-compile",
            "--resolver",
            "backtracking",
            "--strip-extras",
            "-U",
            each.relative_to(ROOT),
        )
