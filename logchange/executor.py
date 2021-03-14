"""
CLI commands executor.
"""
import argparse
import datetime
import logging
from pathlib import Path

from newversion import Version

from logchange.changelog import ChangeLog
from logchange.constants import LATEST, LOGGER_NAME, NEW_CHANGELOG, SECTION_ALL, UNRELEASED
from logchange.eol_fixer import EOLFixer
from logchange.record import Record
from logchange.record_body import RecordBody
from logchange.utils import print_path


class ExecutorError(Exception):
    """
    Main CLI commands executor error.
    """


class Executor:
    """
    CLI commands executor.

    Arguments:
        config -- CLI namespace.
    """

    def __init__(self, config: argparse.Namespace) -> None:
        self._config = config
        self._windows_le = False
        self._logger = logging.getLogger(LOGGER_NAME)

    @property
    def input(self) -> str:
        """
        Pipe-in input.
        """
        self._windows_le = EOLFixer.is_windows(self._config.input)
        return EOLFixer.to_unix(self._config.input)

    @property
    def changelog_path(self) -> Path:
        """
        Path to changelog.
        """
        return self._config.changelog_path

    @staticmethod
    def get_today() -> str:
        """
        Get today date in `YYYY-MM-DD` format.
        """
        return datetime.datetime.now().date().strftime("%Y-%m-%d")

    @property
    def changelog(self) -> ChangeLog:
        """
        Parsed changelog.
        """
        if not self.changelog_path.exists():
            self._logger.warning(f"{print_path(self.changelog_path)} does not exists")
            return ChangeLog.parse(NEW_CHANGELOG)

        text = self.changelog_path.read_text()
        self._windows_le = EOLFixer.is_windows(text)
        return ChangeLog.parse(EOLFixer.to_unix(text))

    def save_changelog(self, changelog: ChangeLog) -> None:
        """
        Save changelog back to `CHANGELOG.md`.

        Arguments:
            changelog -- Changelog to save.
        """
        self.changelog_path.write_text(self._fix_eol(changelog.render()))

    @property
    def release_name(self) -> str:
        return self._config.name

    def _fix_eol(self, text: str) -> str:
        if not self._windows_le:
            return text

        return EOLFixer.to_windows(text)

    @staticmethod
    def _as_md_list(text: str) -> str:
        if not text.strip():
            return text

        if "\n" in text:
            return text

        if text.strip().startswith("-"):
            return text

        return f"- {text}"

    def execute(self) -> str:
        """
        Execute command based on `config`.

        Returns:
            String output.
        """
        commands = {
            "init": self._command_init,
            "add": self._command_add,
            "set": self._command_set,
            "get": self._command_get,
            "format": self._command_format,
            "list": self._command_list,
            "version": self._command_version,
            "rc_version": self._command_rc_version,
            "added": self._command_add_unreleased,
            "changed": self._command_add_unreleased,
            "deprecated": self._command_add_unreleased,
            "removed": self._command_add_unreleased,
            "fixed": self._command_add_unreleased,
            "security": self._command_add_unreleased,
            "release": self._command_release,
        }
        command = self._config.command
        if command not in commands:
            raise ExecutorError(f"Unknown command: {command}")

        return self._fix_eol(commands[self._config.command]())

    def _command_init(self) -> str:
        if not self.changelog_path.exists():
            self.changelog_path.write_text(NEW_CHANGELOG)
            self._logger.info(f"{print_path(self.changelog_path)} created successfully.")
            return ""

        if not self._config.format:
            self._logger.info(
                f"{print_path(self.changelog_path)} already exists." " Add `-f` to reformat it."
            )
            return ""

        text = self.changelog_path.read_text()
        self._windows_le = EOLFixer.is_windows(text)
        changelog = ChangeLog.parse(EOLFixer.to_unix(text))
        changelog.format_released()
        new_text = changelog.render()
        if new_text == text:
            self._logger.info(
                f"{print_path(self.changelog_path)} is good as it is, you are doing great!"
            )
            return ""

        self.changelog_path.write_text(self._fix_eol(changelog.render()))
        self._logger.info(f"{print_path(self.changelog_path)} reformatted.")
        return ""

    def _get_record(self, changelog: ChangeLog, release_name: str) -> Record:
        if release_name == UNRELEASED:
            return changelog.get_unreleased()
        if release_name == LATEST:
            record = changelog.get_latest()
            if record is not None:
                return record
            raise ExecutorError(
                f"No releases found in {print_path(self.changelog_path)}, pass explicit version"
            )

        record = changelog.get_record(Version(release_name))
        if record is not None:
            return record

        self._logger.info(f"Record {release_name} not found, added")
        return Record(Version(release_name), "", self.get_today())

    def _command_add_unreleased(self) -> str:
        self._config.section = self._config.command
        self._config.name = UNRELEASED
        self._config.created = self.get_today()
        return self._command_add()

    def _command_add(self) -> str:
        release_name = self.release_name
        changelog = self.changelog
        record = self._get_record(changelog, release_name)

        if self._config.section == SECTION_ALL:
            record.merge(RecordBody.parse(self.input))
        else:
            section_name = self._config.section
            record.append_section(section_name, self._as_md_list(self.input))

        if self._config.created:
            record.created = self._config.created

        changelog.update_release(record)
        self.save_changelog(changelog)
        return ""

    def _command_set(self) -> str:
        release_name = self.release_name
        changelog = self.changelog
        record = self._get_record(changelog, release_name)

        if self._config.section == SECTION_ALL:
            record.set_body(self.input)
        else:
            section_name = self._config.section
            value = self._as_md_list(self.input)
            record.set_section(section_name, value)

        if self._config.created:
            record.created = self._config.created

        changelog.update_release(record)
        self.save_changelog(changelog)
        return ""

    def _command_get(self) -> str:
        changelog = self.changelog
        record_name = self._config.name
        if record_name == UNRELEASED:
            record = changelog.get_unreleased()
        elif record_name == LATEST:
            record = changelog.get_latest()
        else:
            record = changelog.get_record(Version(record_name))

        if record is None:
            return ""

        if self._config.section == SECTION_ALL:
            return record.render()
        section = record.body.get_section(self._config.section)
        if section:
            return section.body

        return ""

    def _command_format(self) -> str:
        record_body = RecordBody.parse(self.input)
        record_body.sanitize()
        return record_body.render()

    def _command_list(self) -> str:
        records = list(self.changelog.iterate_records())
        return "\n".join([i.version.dumps() for i in records])

    def _command_version(self) -> str:
        old_version: Version = self._config.version
        if self.input:
            record_body = RecordBody.parse(self.input)
        else:
            record_body = self.changelog.get_unreleased().body

        return record_body.bump_version(old_version).dumps()

    def _command_rc_version(self) -> str:
        old_version: Version = self._config.version
        if self.input:
            record_body = RecordBody.parse(self.input)
        else:
            record_body = self.changelog.get_unreleased().body

        return record_body.bump_rc_version(old_version).dumps()

    def _command_release(self) -> str:
        changelog = self.changelog
        record = changelog.get_record(self._config.version)

        if record is None:
            record = Record(self._config.version, "", self.get_today())

        if self._config.created:
            record.created = self._config.created

        unreleased = changelog.get_unreleased()
        record.merge(unreleased.body)
        unreleased.body.clear()

        changelog.update_release(record)
        self.save_changelog(changelog)
        return ""
