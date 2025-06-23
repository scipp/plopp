# Dependency management

plopp is a library, so the package dependencies are never pinned.
Lower bounds are fine and individual versions can be excluded.
See, e.g., [Should You Use Upper Bound Version Constraints](https://iscinumpy.dev/post/bound-version-constraints/) for an explanation.

Development dependencies (as opposed to dependencies of the deployed package that users need to install) are pinned to an exact version in order to ensure reproducibility.
This also includes dependencies used for the various CI builds.
This is done by specifying packages (and potential version constraints) in `requirements/*.in` files and locking those dependencies using [pip-compile-multi](https://pip-compile-multi.readthedocs.io/en/latest/index.html) to produce `requirements/*.txt` files.
Those files are then used by [tox](https://tox.wiki/en/latest/) to create isolated environments and run tests, build docs, etc.

`tox` can be cumbersome to use for local development.
Therefore `requirements/dev.txt` can be used to create a virtual environment with all dependencies.
