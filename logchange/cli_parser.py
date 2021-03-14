"""
Main CLI parser.
"""
import argparse
import sys
from pathlib import Path
from typing import Sequence

import pkg_resources
from newversion import Version, VersionError

from logchange.constants import LATEST, SECTION_ALL, SECTION_TITLES, UNRELEASED
from logchange.utils import dedent


def get_changelog_path(value: str) -> Path:
    """
    Get existing path to "CHANGELOG.md" or to its parent folder.

    Arguments:
        value -- String path.

    Returns:
        Path to file.
    """
    path = Path(value).resolve(strict=False)

    if path.exists() and path.is_dir():
        path = path / "CHANGELOG.md"

    return path


def get_version_latest_or_unreleased(value: str) -> str:
    """
    Get normalized version or latest or unreleased.
    """
    value = value.lower()
    if value == UNRELEASED:
        return value

    if value == LATEST:
        return value

    try:
        return Version(value).dumps()
    except VersionError as e:
        raise argparse.ArgumentTypeError(e) from None


def get_stdin() -> str:
    """
    Get input from stdin.

    Returns:
        Parsed version.
    """
    if sys.stdin.isatty():
        return ""

    return dedent(sys.stdin.read())


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    """
    Main CLI parser.

    Returns:
        Argument parser Namespace.
    """
    try:
        version = pkg_resources.get_distribution("logchange").version
    except pkg_resources.DistributionNotFound:
        version = "0.0.0"

    parser = argparse.ArgumentParser(
        "logchange",
        description="Keep-a-changelog manager",
    )
    parser.add_argument("-V", "--version", action="version", version=version, help="Show version")
    subparsers = parser.add_subparsers(help="Available subcommands", dest="command", required=True)

    parser_init = subparsers.add_parser("init", help="Create CHANGELOG.md")
    parser_init.add_argument(
        "-p",
        "--changelog-path",
        type=Path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )
    parser_init.add_argument(
        "-f",
        "--format",
        action="store_true",
        help="Format existing changelog and write back",
    )

    parser_add = subparsers.add_parser("add", help="Add or update a record in CHANGELOG.md")
    parser_add.add_argument(
        "name",
        type=get_version_latest_or_unreleased,
        default=LATEST,
        help="Release name: version, `latest` or `unreleased`",
    )
    parser_add.add_argument(
        "section",
        help="Section name or `All`",
        nargs="?",
        type=lambda x: x.lower(),
        default=SECTION_ALL,
        choices=[SECTION_ALL, *SECTION_TITLES],
    )
    parser_add.add_argument(
        "-i",
        "--input",
        default=None,
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_add.add_argument(
        "--created",
        default="",
        help="Created date in `YYYY-MM-DD` format.",
    )
    parser_add.add_argument(
        "-p",
        "--changelog-path",
        type=Path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_set = subparsers.add_parser("set", help="Write new or existing record to CHANGELOG.md")
    parser_set.add_argument(
        "name",
        type=get_version_latest_or_unreleased,
        default=LATEST,
        help="Release name: version, `latest` or `unreleased`",
    )
    parser_set.add_argument(
        "section",
        help="Section name or `All`",
        nargs="?",
        type=lambda x: x.lower(),
        default=SECTION_ALL,
        choices=[SECTION_ALL, *SECTION_TITLES],
    )
    parser_set.add_argument(
        "-i",
        "--input",
        default=None,
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_set.add_argument(
        "--created",
        default="",
        help="Created date in `YYYY-MM-DD` format.",
    )
    parser_set.add_argument(
        "-p",
        "--changelog-path",
        type=Path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_get = subparsers.add_parser("get", help="Get changelog record")
    parser_get.add_argument(
        "name",
        nargs="?",
        type=get_version_latest_or_unreleased,
        default=LATEST,
        help="Release name: version, `latest` or `unreleased`",
    )
    parser_get.add_argument(
        "section",
        help="Section name or `All`",
        nargs="?",
        type=lambda x: x.lower(),
        default=SECTION_ALL,
        choices=[SECTION_ALL, *SECTION_TITLES],
    )
    parser_get.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_format = subparsers.add_parser("format", help="Format release notes")
    parser_format.add_argument(
        "-i",
        "--input",
        default=None,
        help="Change notes, can be provided as a pipe-in as well.",
    )

    parser_list = subparsers.add_parser("list", help="List versions")
    parser_list.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_version = subparsers.add_parser(
        "version", help="Bump version according to release notes"
    )
    parser_version.add_argument(
        "version",
        type=Version,
        help="Release version",
    )
    parser_version.add_argument(
        "-i",
        "--input",
        default=None,
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_version.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_rc_version = subparsers.add_parser(
        "rc_version", help="Bump RC version according to release notes"
    )
    parser_rc_version.add_argument(
        "version",
        type=Version,
        help="Release version",
    )
    parser_rc_version.add_argument(
        "-i",
        "--input",
        default=None,
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_rc_version.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_added = subparsers.add_parser("added", help="Add entry to Unreleased Added section")
    parser_added.add_argument(
        "input",
        nargs="*",
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_added.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_changed = subparsers.add_parser(
        "changed", help="Add entry to Unreleased Changed section"
    )
    parser_changed.add_argument(
        "input",
        nargs="*",
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_changed.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_deprecated = subparsers.add_parser(
        "deprecated", help="Add entry to Unreleased Deprecated section"
    )
    parser_deprecated.add_argument(
        "input",
        nargs="*",
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_deprecated.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_removed = subparsers.add_parser(
        "removed", help="Add entry to Unreleased Removed section"
    )
    parser_removed.add_argument(
        "input",
        nargs="*",
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_removed.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_fixed = subparsers.add_parser("fixed", help="Add entry to Unreleased Fixed section")
    parser_fixed.add_argument(
        "input",
        nargs="*",
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_fixed.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_security = subparsers.add_parser(
        "security", help="Add entry to Unreleased Security section"
    )
    parser_security.add_argument(
        "input",
        nargs="*",
        help="Change notes, can be provided as a pipe-in as well.",
    )
    parser_security.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )

    parser_release = subparsers.add_parser(
        "release", help="Convert Unreleased section to a new release"
    )
    parser_release.add_argument(
        "version",
        type=Version,
        help="Release version.",
    )
    parser_release.add_argument(
        "-p",
        "--changelog-path",
        type=get_changelog_path,
        default=Path.cwd() / "CHANGELOG.md",
        help="Full path to changelog file. Default: ./CHANGELOG.md",
    )
    parser_release.add_argument(
        "--created",
        default="",
        help="Created date in `YYYY-MM-DD` format.",
    )

    result = parser.parse_args(args)
    if hasattr(result, "input"):
        if isinstance(result.input, list):
            result.input = " ".join(result.input)
        if not result.input:
            result.input = get_stdin()

    return result
