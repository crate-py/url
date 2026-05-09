from pathlib import Path
from tempfile import TemporaryDirectory

import nox

ROOT = Path(__file__).parent
PYPROJECT = ROOT / "pyproject.toml"
DOCS = ROOT / "docs"
TESTS = ROOT / "tests"

SUPPORTED = ["3.10", "pypy3.11", "3.11", "3.12", "3.13", "3.14"]
LATEST = SUPPORTED[-1]

nox.options.default_venv_backend = "uv"
nox.options.sessions = []


def session(default=True, python=LATEST, **kwargs):  # noqa: D103
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(python=python, **kwargs)(fn)

    return _session


def sync(session, group):
    """
    Populate the active session venv from a uv dependency group.
    """
    session.run_install(
        "uv",
        "sync",
        "--active",
        "--no-default-groups",
        "--group",
        group,
        external=True,
    )


@session(python=SUPPORTED)
def tests(session):
    """
    Run the test suite with a corresponding Python version.
    """
    sync(session, "tests")
    session.run("pytest", *session.posargs, TESTS)


@session(tags=["build"])
def build(session):
    """
    Build a distribution suitable for PyPI and check its validity.
    """
    sync(session, "packaging")
    with TemporaryDirectory() as tmpdir:
        session.run("python", "-m", "build", ROOT, "--outdir", tmpdir)
        session.run("twine", "check", "--strict", tmpdir + "/*")


@session(tags=["style"])
def style(session):
    """
    Check Python code style.
    """
    sync(session, "style")
    session.run("ruff", "check", TESTS, __file__)


@session()
def typing(session):
    """
    Check the codebase using pyright by type checking the test suite.
    """
    sync(session, "typing")
    session.run("pyright", TESTS)


@session(tags=["docs"])
@nox.parametrize(
    "builder",
    [
        nox.param(name, id=name)
        for name in [
            "dirhtml",
            "doctest",
            "linkcheck",
            "man",
            "spelling",
        ]
    ],
)
def docs(session, builder):
    """
    Build the documentation using a specific Sphinx builder.
    """
    sync(session, "docs")
    with TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        argv = ["-n", "-T", "-W"]
        if builder != "spelling":
            argv += ["-q"]
        posargs = session.posargs or [tmpdir / builder]
        session.run(
            "python",
            "-m",
            "sphinx",
            "-b",
            builder,
            DOCS,
            *argv,
            *posargs,
        )


@session(tags=["docs", "style"], name="docs(style)")
def docs_style(session):
    """
    Check the documentation style.
    """
    sync(session, "docs-style")
    session.run("python", "-m", "doc8", "--config", PYPROJECT, DOCS)
