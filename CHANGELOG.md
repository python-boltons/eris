# Changelog for `eris`

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to
[Semantic Versioning].

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/


## [Unreleased](https://github.com/python-boltons/eris/compare/0.2.2...HEAD)

No notable changes have been made.


## [0.2.2](https://github.com/python-boltons/eris/compare/0.2.1...0.2.2) - 2021-12-24

### Changed

* Represent all `ExcInfo` objects as dictionaries.
* Make `AbstractResult` apart of public API.


## [0.2.1](https://github.com/python-boltons/eris/compare/0.2.0...0.2.1) - 2021-12-23

### Changed

* The `Err` `dataclass` now accepts an optional `up` kwarg.


## [0.2.0](https://github.com/python-boltons/eris/compare/0.1.2...0.2.0) - 2021-12-23

### Changed

* Allow custom sub-types of `ErisError` to be used with the `Result` type.
* *BREAKING CHANGE*: The `Err` type is now a generic with two type variables.


## [0.1.2](https://github.com/python-boltons/eris/compare/0.1.1...0.1.2) - 2021-12-23

### Changed

* Add `eris.ErisErrorChain` and `eris.ErisErrorDict` to public API.

### Removed

* Remove `eris.chain_errors()` public API function.


## [0.1.1](https://github.com/python-boltons/eris/compare/0.1.0...0.1.1) - 2021-12-22

### Changed

* Rename `Error` to `ErisError`.


## [0.1.0](https://github.com/python-boltons/eris/releases/tag/0.1.0) - 2021-12-22

### Miscellaneous

* Port `eris` library from (original) `bugyi-lib` library.
* First release.
