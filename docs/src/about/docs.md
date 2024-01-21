## Overview

<p class="intro" markdown>

You will need to set up a Python environment to create, test, and preview docs changes.

</p>

---

## Modifying Docs

If you plan to make changes to this documentation, you will need to install the following dependencies first:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

Once done, you should clone this repository:

```bash linenums="0"
git clone https://github.com/reactive-python/reactpy-router.git
cd reactpy-router
```

Then, by running the command below you can:

-   Install an editable version of the documentation
-   Self-host a test server for the documentation

```bash linenums="0"
pip install -r requirements.txt --upgrade
```

Finally, to verify that everything is working properly, you can manually run the docs preview web server.

```bash linenums="0"
cd docs
mkdocs serve
```

Navigate to [`http://127.0.0.1:8000`](http://127.0.0.1:8000) to view a preview of the documentation.

## Creating a pull request

{% include-markdown "../../includes/pr.md" %}
