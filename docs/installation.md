# Installation

## Stable release

To install module-utilities, run this command in your terminal:

```bash
pip install module_utilities
```

or

```bash
conda install -c wpk-nist module_utilities
```

This is the preferred method to install module-utilities, as it
will always install the most recent stable release.

## From sources

The sources for module-utilities can be downloaded from the
[Github repo].

You can either clone the public repository:

```bash
git clone git://github.com/wpk-nist-gov/module-utilities.git
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

where options in brackets are options (for environment name, and editable install, repectively).

[github repo]: https://github.com/wpk-nist-gov/module-utilities
