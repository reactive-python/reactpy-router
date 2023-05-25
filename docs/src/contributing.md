# Contributing

!!! note

    The [Code of Conduct](https://github.com/reactive-python/reactpy/blob/main/CODE_OF_CONDUCT.md)
    applies in all community spaces. If you are not familiar with our Code of Conduct policy,
    take a minute to read it before making your first contribution.

The ReactPy team welcomes contributions and contributors of all kinds - whether they
come as code changes, participation in the discussions, opening issues and pointing out
bugs, or simply sharing your work with your colleagues and friends. We’re excited to see
how you can help move this project and community forward!

## Everyone Can Contribute!

Trust us, there’s so many ways to support the project. We’re always looking for people who can:

- Improve our documentation
- Teach and tell others about ReactPy
- Share ideas for new features
- Report bugs
- Participate in general discussions

Still aren’t sure what you have to offer? Just [ask us](https://github.com/reactive-python/reactpy-router/discussions) and we’ll help you make your first contribution.

## Development Environment

For a developer installation from source be sure to install
[NPM](https://www.npmjs.com/) before running:

```bash
git clone https://github.com/reactive-python/reactpy-router
cd reactpy-router
pip install -e . -r requirements.txt
```

This will install an ediable version of `reactpy-router` as well as tools you'll need
to work with this project.

Of particular note is [`nox`](https://nox.thea.codes/en/stable/), which is used to
automate testing and other development tasks.

## Running the Tests

```bash
nox -s test
```

You can run the tests with a headed browser.

```bash
nox -s test -- --headed
```

## Releasing This Package

To release a new version of reactpy-router on PyPI:

1. Install [`twine`](https://twine.readthedocs.io/en/latest/) with `pip install twine`
2. Update the `version = "x.y.z"` variable in `reactpy-router/__init__.py`
3. `git` add the changes to `__init__.py` and create a `git tag -a x.y.z -m 'comment'`
4. Build the Python package with `python setup.py sdist bdist_wheel`
5. Check the build artifacts `twine check --strict dist/*`
6. Upload the build artifacts to [PyPI](https://pypi.org/) `twine upload dist/*`

To release a new version of `reactpy-router` on [NPM](https://www.npmjs.com/):

1. Update `js/package.json` with new npm package version
2. Clean out prior builds `git clean -fdx`
3. Install and publish `npm install && npm publish`
