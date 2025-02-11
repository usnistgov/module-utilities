<!-- markdownlint-disable MD041 -->

<!-- prettier-ignore-start -->
[![Repo][repo-badge]][repo-link]
[![Docs][docs-badge]][docs-link]
[![PyPI license][license-badge]][license-link]
[![PyPI version][pypi-badge]][pypi-link]
[![Conda (channel only)][conda-badge]][conda-link]
[![Code style: ruff][ruff-badge]][ruff-link]
[![uv][uv-badge]][uv-link]

<!--
  For more badges, see
  https://shields.io/category/other
  https://naereen.github.io/badges/
  [pypi-badge]: https://badge.fury.io/py/module-utilities
-->

[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff-link]: https://github.com/astral-sh/ruff
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[uv-link]: https://github.com/astral-sh/uv
[pypi-badge]: https://img.shields.io/pypi/v/module-utilities
[pypi-link]: https://pypi.org/project/module-utilities
[docs-badge]: https://img.shields.io/badge/docs-sphinx-informational
[docs-link]: https://pages.nist.gov/module-utilities/
[repo-badge]: https://img.shields.io/badge/--181717?logo=github&logoColor=ffffff
[repo-link]: https://github.com/usnistgov/module-utilities
[conda-badge]: https://img.shields.io/conda/v/conda-forge/module-utilities
[conda-link]: https://anaconda.org/conda-forge/module-utilities
[license-badge]: https://img.shields.io/pypi/l/module-utilities?color=informational
[license-link]: https://github.com/usnistgov/module-utilities/blob/main/LICENSE

<!-- other links -->

[cachetools]: https://github.com/tkem/cachetools/

<!-- prettier-ignore-end -->

# `module-utilities`

A Python package for creating python modules.

## Overview

I was using the same code snippets over and over, so decided to put them in one
place.

## Features

- `cached`: A module to cache class attributes and methods. Right now, this uses
  a standard python dictionary for storage. Future versions will hopefully
  integrate with something like [cachetools].

- `docfiller`: A module to share documentation. This is adapted from the
  [pandas `doc` decorator](https://github.com/pandas-dev/pandas/blob/main/pandas/util/_decorators.py).
  There are some convenience functions and classes for sharing documentation.

- `docinhert`: An interface to [docstring-inheritance] module. This can be
  combined with `docfiller` to make creating related function/class
  documentation easy.

[docstring-inheritance]: https://github.com/AntoineD/docstring-inheritance

## Status

This package is actively used by the author. Please feel free to create a pull
request for wanted features and suggestions!

## Example usage

Simple example of using `cached` module.

```pycon
>>> from module_utilities import cached
>>>
>>> class Example:
...     @cached.prop
...     def aprop(self):
...         print("setting prop")
...         return ["aprop"]
...     @cached.meth
...     def ameth(self, x=1):
...         print("setting ameth")
...         return [x]
...     @cached.clear
...     def method_that_clears(self):
...         pass
...
>>> x = Example()
>>> x.aprop
setting prop
['aprop']
>>> x.aprop
['aprop']

>>> x.ameth(1)
setting ameth
[1]
>>> x.ameth(x=1)
[1]

>>> x.method_that_clears()

>>> x.aprop
setting prop
['aprop']
>>> x.ameth(1)
setting ameth
[1]

```

Simple example of using `DocFiller`.

```pycon
>>> from module_utilities.docfiller import DocFiller, indent_docstring
>>> d = DocFiller.from_docstring(
...     """
...     Parameters
...     ----------
...     x : int
...         x param
...     y : int
...         y param
...     z0 | z : int
...         z int param
...     z1 | z : float
...         z float param
...
...     Returns
...     -------
...     output0 | output : int
...         Integer output.
...     output1 | output : float
...         Float output
...     """,
...     combine_keys="parameters",
... )
>>> @d.decorate
... def func(x, y, z):
...     """
...     Parameters
...     ----------
...     {x}
...     {y}
...     {z0}
...
...     Returns
...     --------
...     {returns.output0}
...     """
...     return x + y + z
...
>>> print(indent_docstring(func))
+  Parameters
+  ----------
+  x : int
+      x param
+  y : int
+      y param
+  z : int
+      z int param
<BLANKLINE>
+  Returns
+  --------
+  output : int
+      Integer output.

# Note that for python version <= 3.8 that method chaining
# in decorators doesn't work, so have to do the following.
# For newer python, you can inline this.
>>> dd = d.assign_keys(z="z0", out="returns.output0")
>>> @dd.decorate
... def func1(x, y, z):
...     """
...     Parameters
...     ----------
...     {x}
...     {y}
...     {z}
...     Returns
...     -------
...     {out}
...     """
...     pass
...
>>> print(indent_docstring(func1))
+  Parameters
+  ----------
+  x : int
+      x param
+  y : int
+      y param
+  z : int
+      z int param
+  Returns
+  -------
+  output : int
+      Integer output.

>>> dd = d.assign_keys(z="z1", out="returns.output1")
>>> @dd(func1)
... def func2(x, y, z):
...     pass
...

>>> print(indent_docstring(func2))
+  Parameters
+  ----------
+  x : int
+      x param
+  y : int
+      y param
+  z : float
+      z float param
+  Returns
+  -------
+  output : float
+      Float output


```

<!-- end-docs -->

## Installation

<!-- start-installation -->

Use one of the following

```bash
pip install module-utilities
```

or

```bash
conda install -c conda-forge module-utilities
```

Optionally, you can install [docstring-inheritance] to use the `docinherit`
module:

```bash
pip install docstring-inheritance
# or
conda install -c conda-forge docstring-inheritance
```

<!-- end-installation -->

## Documentation

See the [documentation][docs-link] for a look at `module-utilities` in action.

## License

This is free software. See [LICENSE][license-link].

## Related work

`module-utilities` is used in the following packages

- [cmomy]
- [analphipy]
- [tmmc-lnpy]
- [thermoextrap]

[cmomy]: https://github.com/usnistgov/cmomy
[analphipy]: https://github.com/usnistgov/analphipy
[tmmc-lnpy]: https://github.com/usnistgov/tmmc-lnpy
[thermoextrap]: https://github.com/usnistgov/thermoextrap

## Contact

The author can be reached at <wpk@nist.gov>.

## Credits

This package was created using
[Cookiecutter](https://github.com/audreyr/cookiecutter) with the
[usnistgov/cookiecutter-nist-python](https://github.com/usnistgov/cookiecutter-nist-python)
template.
