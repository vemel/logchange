# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[PEP 440 -- Version Identification and Dependency Specification](https://www.python.org/dev/peps/pep-0440/).

## [Unreleased]

## [0.1.2rc1] - 2021-02-26
### Added
- `added <text>` CLI command to update `Unreleased` section
- `changed <text>` CLI command to update `Unreleased` section
- `deprecated <text>` CLI command to update `Unreleased` section
- `removed <text>` CLI command to update `Unreleased` section
- `fixed <text>` CLI command to update `Unreleased` section
- `security <text>` CLI command to update `Unreleased` section
- `release <version>` CLI command to move `Unreleased` section to release notes

### Changed
- Release notes can now have text other than keep-a-changelog entries
- `get` command no longer raises an error on non-existing `CHANGELOG.md`
- Added support for Python 3.6.10+

### Fixed
- Empty releases were not added to changelog
- Codeblocks are no longer removed from release notes
- Indented sections were not parsed properly

## [0.1.1] - 2021-02-26
Initial release
