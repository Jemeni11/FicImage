# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[//]: # (Types of changes)
[//]: # (- **Added** for new features.)
[//]: # (- **Changed** for changes in existing functionality.)
[//]: # (- **Deprecated** for soon-to-be removed features.)
[//]: # (- **Removed** for now removed features.)
[//]: # (- **Fixed** for any bug fixes.)
[//]: # (- **Security** in case of vulnerabilities.)


## [2.1.0] - 2023-07-22

### Fixed
- [Issue #4](https://github.com/Jemeni11/FicImage/issues/4). Replaced manual string splitting/joining code 
with os.path functions.
- Syntax error in PYPI_README.rst. 

### Changed
- Uncommented out the `[project]` and `[project-urls]` sections in `pyproject.toml` 
as they are not redundant anymore. 


## [2.0.0] - 2023-07-22

### Fixed
- [Issue #2](https://github.com/Jemeni11/FicImage/issues/2). A bug in the file path of the `load_config_json` function caused a `FileNotFoundError`. 

### Added
- Added a new `except` block to the `load_config_json` function. 
This should make finding errors like [Issue #2](https://github.com/Jemeni11/FicImage/issues/2) easier.
- Added a new command (-v) to return the project version.
- Added a new command (-r) to update all files in the directory path given and its subdirectories.

### Changed
- Moved the project version from `__init__.py` to `main.py`.
- `path_to_epub` is now an optional command.
- FicImage will now save new epubs in the same location 
as the old epub instead of the current working directory.

## [1.0.2] - 2023-05-12

### Added

- Added the project version to `__init__.py`.
- Created a README file for PyPI (PYPI_README.rst). 
This file replaces the old README file as the long description for the package.
The old README still exists as `README.md` and is still used for GitHub.

### Changed
- Updated the file paths in `setup.py` and `pyproject.toml` to point to 
the new `PYPI_README.rst` file. 
- Commented out the `[project]` and `[project-urls]` sections in `pyproject.toml` 
as they were redundant. 

### Fixed
- Fixed the long description content type in `setup.py` and `pyproject.toml` to 
match the new README format. The content type was updated from `text/markdown` to `text/x-rst`.

## [1.0.1] - 2023-05-11

### Added
- Improved logging by adding an overview of downloaded images.
- Added a Changelog

## [1.0.0] - 2023-05-08
- Released FicImageScript


[2.1.0]: https://github.com/Jemeni11/FicImage/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/Jemeni11/FicImage/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/Jemeni11/FicImage/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/Jemeni11/FicImage/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Jemeni11/FicImage/releases/tag/v1.0.0
