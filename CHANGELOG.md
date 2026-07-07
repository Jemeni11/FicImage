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

## [5.0.0] - TBD

### Added

- ZIP support alongside EPUB (with base64 embedding or filesystem image modes)
- FicHub detection: automatically validates files are from FicHub before processing
- Image summary reports: shows download success/failure stats after processing
- CLI enhancements: `--verbose`, `--update`, and `--credits` flags
- ZIP embedding option: `zip_embed_images` config to choose between base64 or file-based images
- New project logo
- `py.typed` marker (PEP 561) for downstream type-checkers
- `.python-version` file (Python 3.14) for uv/pyenv integration
- Ruff linting config covering 15 rule sets (F, W, E, I, UP, C4, ISC, ICN, RET, SIM, TID, TC, PTH, TD, FURB, B)
- `ty` type-checker config
- GitHub CI workflow: ruff check/format + ty on Python 3.12, 3.13, 3.14
- pre-commit config with ruff, ty, and file hygiene hooks
- GitHub FUNDING.yml (Sponsors, Polar, Buy Me a Coffee)

### Changed

- **BREAKING:** Default image format changed from JPEG to WEBP
- **BREAKING:** Default max image size reduced from 1MB to 100KB
- **BREAKING:** CLI argument changed from `-p/--path_to_epub` to `-p/--path`
- **BREAKING:** Package restructured to `src/` layout; import paths changed accordingly
- **BREAKING:** Entry point renamed from `FicImageScript.main:main` to `ficimagescript.main:main`
- **BREAKING:** Minimum Python version raised from 3.9 to 3.12
- Switched build backend from setuptools to `uv_build`
- Replaced `requests`/`urllib3`/`certifi` HTTP stack with `httpx`/`httpcore`/`h11`/`anyio`
- Replaced `os.path` with `pathlib.Path` throughout
- Refactored monolithic `utils.py` into `utils/{files,logging,update}.py`
- Consolidated global state and config into `config.py`
- Organized format handlers under `formats/` subpackage
- Centralized config via global state dictionary (no more parameter passing everywhere)
- Only creates output files when at least one image is downloaded
- Improved error handling for failed image downloads and corrupted files
- Better cross-platform path handling (fixed Windows backslash issues)
- Bumped all dependency floor versions (beautifulsoup4≥4.15, lxml≥6.1.1, packaging≥26.2, pillow≥12.2)
- Replaced `requirements.txt` with `uv.lock` + `pyproject.toml` for dependency management
- README: added "Why no PDF/MOBI support?" section with rationale, removed from Planned Features

### Removed

- PDF and MOBI support; users are directed to use an EPUB source and convert with Calibre instead
- Unused ZIP helper functions: `copy_zip()`, `extract_zip_metadata()`, `create_images_dir()`, `clean_images_dir()`
- `pymupdf` dependency (PDF rendering library)
- `six` dependency (Python 2 compatibility shim)
- `requirements.txt` (replaced by uv-managed lockfile)

### Fixed

- `UnidentifiedImageError` now caught during image processing
- Standardized verbose and config-check logging output
- Crash when `get_image_from_url()` returns `None` — proper result validation added before unpacking
- Non-embed ZIP mode now writes images with correct relative paths (`images/…`)
- Windows path separator issues in ZIP image references (always uses forward slashes)

## [4.1.1] - 2024-09-18

### Changed

- Changed the build system.

## [4.1.0] - 2024-04-17

### Added

- Added a user agent string to help download imgur images.

## [4.0.0] - 2024-02-28

### Fixed

- Fixed major file path issue preventing Windows users from using FicImage.

## [3.0.0] - 2023-10-30

### Security

- Updated the `requests` dependency to ensure compatibility with version 2.31.0 or higher to
  mitigate [CVE-2023-32681](https://nvd.nist.gov/vuln/detail/CVE-2023-32681) security issue.

### Changed

- Modified requirements to use "compatible with" (>=) instead of "exact version" (==) when installing to prevent
  potential conflicts with previously installed software.

## [2.1.0] - 2023-07-22

### Fixed

- [Issue #4](https://github.com/Jemeni11/FicImage/issues/4). Replaced manual string splitting/joining code
  with `os.path` functions.
- Syntax error in PYPI_README.rst.

### Changed

- Uncommented out the `[project]` and `[project-urls]` sections in `pyproject.toml`
  as they are not redundant anymore.

## [2.0.0] - 2023-07-22

### Fixed

- [Issue #2](https://github.com/Jemeni11/FicImage/issues/2). A bug in the file path of the `load_config_json` function
  caused a `FileNotFoundError`.

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

[5.0.0]: https://github.com/Jemeni11/FicImage/compare/v4.1.1...v5.0.0

[4.1.1]: https://github.com/Jemeni11/FicImage/compare/v4.1.0...v4.1.1

[4.1.0]: https://github.com/Jemeni11/FicImage/compare/v4.0.0...v4.1.0

[4.0.0]: https://github.com/Jemeni11/FicImage/compare/v3.0.0...v4.0.0

[3.0.0]: https://github.com/Jemeni11/FicImage/compare/v2.1.0...v3.0.0

[2.1.0]: https://github.com/Jemeni11/FicImage/compare/v2.0.0...v2.1.0

[2.0.0]: https://github.com/Jemeni11/FicImage/compare/v1.0.2...v2.0.0

[1.0.2]: https://github.com/Jemeni11/FicImage/compare/v1.0.1...v1.0.2

[1.0.1]: https://github.com/Jemeni11/FicImage/compare/v1.0.0...v1.0.1

[1.0.0]: https://github.com/Jemeni11/FicImage/releases/tag/v1.0.0
