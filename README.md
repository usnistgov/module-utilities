<!-- markdownlint-disable MD041 -->

[![Repo][repo-badge]][repo-link] [![Docs][docs-badge]][docs-link]
[![PyPI license][license-badge]][license-link]
[![PyPI version][pypi-badge]][pypi-link]
[![Conda (channel only)][conda-badge]][conda-link]
[![Code style: black][black-badge]][black-link]

<!--
  For more badges, see
  https://shields.io/category/other
  https://naereen.github.io/badges/
  [pypi-badge]: https://badge.fury.io/py/module-utilities
-->

[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/psf/black
[pypi-badge]: https://img.shields.io/pypi/v/module-utilities
[pypi-link]: https://pypi.org/project/module-utilities
[docs-badge]: https://img.shields.io/badge/docs-sphinx-informational
[docs-link]: https://pages.nist.gov/module-utilities/
[repo-badge]: https://img.shields.io/badge/--181717?logo=github&logoColor=ffffff
[repo-link]: https://github.com/wpk-nist-gov/module-utilities
[conda-badge]: https://img.shields.io/conda/v/wpk-nist/module-utilities
[conda-link]: https://anaconda.org/wpk-nist/module-utilities
[license-badge]: https://img.shields.io/pypi/l/cmomy?color=informational
[license-link]:
  https://github.com/wpk-nist-gov/module-utilities/blob/main/LICENSE

<!-- other links -->

[cachetools]: https://github.com/tkem/cachetools/

# `module-utilities`

A Python package for creating python modules.

## Overview

I was using the same code snippets over and over, so decided to put them in one
place.

## Features

- `cached`: A module to cache class attributes and methods. Right now, this uses
  a standard python dictionary for storage. Future versions will hopefully
  integrate with something like [cachetools].

- `docfiller`: A module to share documentation. This is addapted from the
  [pandas `doc` decorator](https://github.com/pandas-dev/pandas/blob/main/pandas/util/_decorators.py).
  There are some convenience functions and classes for sharing documentation.

## Status

This package is actively used by the author. Please feel free to create a pull
request for wanted features and suggestions!

## Quick start

Use one of the following

```bash
pip install module-utilities
```

or

```bash
conda install -c wpk-nist module-utilities
```

## Example usage

```python
import module_utilities

```

<!-- end-docs -->

## Documentation

See the [documentation][docs-link] for a look at `module-utilities` in action.

## License

This is free software. See [LICENSE][license-link].

## Related work

Any other stuff to metion....

## Contact

The author can be reached at wpk@nist.gov.

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[wpk-nist-gov/cookiecutter-pypackage](https://github.com/wpk-nist-gov/cookiecutter-pypackage)
Project template forked from
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).
