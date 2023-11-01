<!-- markdownlint-disable MD024 -->
<!-- markdownlint-disable MD013 -->
<!-- prettier-ignore-start -->
# Changelog

Changelog for `module-utilities`

## Unreleased

[changelog.d]: https://github.com/usnistgov/module-utilities

See the fragment files in [changelog.d]

<!-- prettier-ignore-end -->

<!-- markdownlint-enable MD013 -->

<!-- scriv-insert-here -->

## v0.9.0 — 2023-08-22

### Changed

- Revert to TypeVar `S` being invariant. This leads to some issues with
  `cached.prop` decorator. However, the use of covariant `TypeVar` was a hack.
  Instead, it is better in these cases to decorate with `@property` on top of
  `@cached.meth`. mypy/pyright deal with `property` in a special way.
- To better work with the above, single parameter methods are caached using only
  the method name, and no parameters.

## v0.8.0 — 2023-08-21

### Changed

- Moved submodule `_typing` to `typing` (i.e., publicly accessible).
- Made TypeVar `S` covariant. This fixes issues with subclassing overrides.

## v0.7.0 — 2023-08-15

### Changed

- Simplified cached.prop by using (new) CachedProperty class.

## v0.6.0 — 2023-08-01

### Added

- Now include module `docinhert` to interface with
  [docstring-inheritance](https://github.com/AntoineD/docstring-inheritance)
- Fully support mypy and pyright type checking.

## v0.5.0 — 2023-07-10

### Added

See the fragment files in [changelog.d]

<!-- prettier-ignore-end -->

- Add `_prepend` option to docfiller. Default behavior is now to append current
docstring to templates.
<!-- markdownlint-enable MD013 -->

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
