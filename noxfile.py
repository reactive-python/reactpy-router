from pathlib import Path

from nox import Session, session

ROOT_DIR = Path(__file__).parent


@session(tags=["test"])
def test_python(session: Session) -> None:
    install_requirements_file(session, "test-env")
    session.install(".[all]")
    session.run("playwright", "install", "chromium")

    posargs = session.posargs[:]
    session.run("pytest", "tests", *posargs)


@session(tags=["test"])
def test_types(session: Session) -> None:
    install_requirements_file(session, "check-types")
    install_requirements_file(session, "pkg-deps")
    session.run("mypy", "--show-error-codes", "src/reactpy_router", "tests")


@session(tags=["test"])
def test_style(session: Session) -> None:
    install_requirements_file(session, "check-style")
    session.run("black", ".", "--check")
    session.run("ruff", "check", ".")


@session(tags=["test"])
def test_javascript(session: Session) -> None:
    session.chdir(ROOT_DIR / "src" / "js")
    session.run("python", "-m", "nodejs.npm", "install", external=True)
    session.run("python", "-m", "nodejs.npm", "run", "check")


def install_requirements_file(session: Session, name: str) -> None:
    session.install("--upgrade", "pip", "setuptools", "wheel")
    file_path = ROOT_DIR / "requirements" / f"{name}.txt"
    assert file_path.exists(), f"requirements file {file_path} does not exist"
    session.install("-r", str(file_path))
