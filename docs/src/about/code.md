## Overview

<p class="intro" markdown>

    You will need to set up a Python environment to develop ReactPy-Router.

</p>

---

## Creating an environment

If you plan to make code changes to this repository, you will need to install the following dependencies first:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

Once done, you should clone this repository:

```bash linenums="0"
git clone https://github.com/reactive-python/reactpy-router.git
cd reactpy-router
```

Then, by running the command below you can install the dependencies needed to run the ReactPy-Router development environment.

```bash linenums="0"
pip install -r requirements.txt --upgrade --verbose
```

## Running the full test suite

!!! abstract "Note"

    This repository uses [Nox](https://nox.thea.codes/en/stable/) to run tests. For a full test of available scripts run `nox -l`.

By running the command below you can run the full test suite:

```bash linenums="0"
nox -t test
```

Or, if you want to run the tests in the foreground with a visible browser window, run:

<!-- TODO: Change `headed` to `headless` -->

```bash linenums="0"
nox -t test -- --headed
```

## Creating a pull request

{% include-markdown "../../includes/pr.md" %}
