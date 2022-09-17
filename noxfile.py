from pathlib import Path

from nox import Session, session

ROOT = Path(".")
REQUIREMENTS_DIR = ROOT / "requirements"


@session
def format(session: Session) -> None:
    install_requirements(session, "style")
    session.run("black", ".")
    session.run("isort", ".")


@session
def test(session: Session) -> None:
    session.notify("test_style")
    session.notify("test_types")
    session.notify("test_suite")


@session
def test_style(session: Session) -> None:
    install_requirements(session, "check-style")
    session.run("black", "--check", ".")
    session.run("isort", "--check", ".")
    session.run("flake8", ".")


@session
def test_types(session: Session) -> None:
    install_requirements(session, "check-types")
    session.run("mypy", "--strict", "idom_router")


@session
def test_suite(session: Session) -> None:
    install_requirements(session, "test-env")
    session.run("playwright", "install", "chromium")

    posargs = session.posargs[:]

    if "--no-cov" in session.posargs:
        posargs.remove("--no-cov")
        session.log("Coverage won't be checked")
        session.install(".")
    else:
        posargs += ["--cov=idom_router", "--cov-report=term"]
        session.install("-e", ".")

    session.run("pytest", "tests", *posargs)


def install_requirements(session: Session, name: str) -> None:
    session.install("-r", str(REQUIREMENTS_DIR / f"{name}.txt"))
