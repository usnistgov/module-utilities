<!-- markdownlint-disable MD024 -->

# Changelog

Changelog for `module-utilities`

## Unreleased

See the fragment files in
[changelog.d](https://github.com/usnistgov/module-utilities)

<!-- scriv-insert-here -->

## v0.6.0 — 2023-08-01

### Added

- Now include module `docinhert` to interface with
  [docstring-inheritance](https://github.com/AntoineD/docstring-inheritance)
- Fully support mypy and pyright type checking.

## v0.5.0 — 2023-07-10

### Added

- Add `_prepend` option to docfiller. Default behavior is now to append current
  docstring to templates.

## v0.4.0 — 2023-06-14

### Added

- Package now available on conda-forge

### Changed

- Properly vendor numpydocs and include pointer to license

## v0.3.0 — 2023-05-03

### Added

- Added `DocFiller.assign_param` to more easily add a new parameter.

## v0.2.0 — 2023-05-02

### Added

- Added method `assign_keys` to `DocFiller`.

## v0.1.0 — 2023-05-01

### Added

- Add typing support. Passing mypy, pyright, pytype.
