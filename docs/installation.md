# Installation

## Stable release

To install module-utilities, run this command in your terminal:

```bash
pip install module-utilities
```

or

```bash
conda install -c conda-forge module-utilities
```

This is the preferred method to install module-utilities, as it will always
install the most recent stable release.

Optionally, you can install
[docstring-inheritance](https://github.com/AntoineD/docstring-inheritance) with

```base
pip install docstring-inheritance
# or
conda install -c conda-forge docstring-inheritance
```

## From sources

The sources for module-utilities can be downloaded from the [Github repo].

You can either clone the public repository:

```bash
git clone git://github.com/usnistgov/module-utilities.git
```

Once you have a copy of the source, you can install it with:

```bash
pip install .
```

To install dependencies with conda/mamba, use:

```bash
conda env create [-n {name}] -f environment.yaml
conda activate {name}
pip install [-e] --no-deps .
```

where options in brackets are options (for environment name, and editable
install, respectively).

[github repo]: https://github.com/usnistgov/module-utilities
