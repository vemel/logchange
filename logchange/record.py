"""
Release record.
"""
import logging
from typing import Optional, Tuple, Type, TypeVar

from newversion import Version

from logchange.constants import LOGGER_NAME, SECTION_TITLES
from logchange.record_body import RecordBody
from logchange.record_section import RecordSection
from logchange.utils import dedent

_R = TypeVar("_R", bound="Record")


class Record:
    """
    Release record.

    Arguments:
        version -- Release version
        text -- Release notes
        created -- Release date
    """

    PARTS_DELIM = "\n"

    def __init__(
        self,
        version: Version,
        text: str,
        created: str,
    ):
        self._logger = logging.getLogger(LOGGER_NAME)
        self.version: Version = version
        self.created: str = created
        self._text = text
        self._record_body: Optional[RecordBody] = None

    @property
    def name(self) -> str:
        """
        Release version as tag.
        """
        if self.version == Version.zero():
            return "[Unreleased]"

        return f"[{self.version.dumps()}]"

    @property
    def body(self) -> RecordBody:
        """
        Release body.
        """
        if self._record_body is None:
            self._record_body = RecordBody.parse(self._text)

        return self._record_body

    @body.setter
    def body(self, value: RecordBody):
        self._record_body = value

    def _render_title(self) -> str:
        if self.version == Version.zero():
            return "## [Unreleased]"

        if self.created:
            return f"## [{self.version}] - {self.created}"

        return f"## [{self.version}]"

    def render(self) -> str:
        """
        Render as text.
        """
        body = self._text
        if self._record_body:
            body = self._record_body.render()
        parts = [self._render_title(), body]
        parts = [i for i in parts if i]
        return self.PARTS_DELIM.join(parts)

    @staticmethod
    def _parse_title(title: str) -> Tuple[str, str]:
        title_parts = title.split()
        version = (
            title_parts[1].replace("[", "").replace("]", "") if len(title_parts) > 1 else "0.0.0"
        )
        created = title_parts[3] if len(title_parts) > 3 else ""
        return (version, created)

    @classmethod
    def parse(cls: Type[_R], text: str) -> _R:
        """
        Parse from text.

        Arguments:
            text -- Record text to parse.

        Returns:
            New Record.
        """
        text = dedent(text)
        if not text:
            return cls(Version.zero(), created="", text="")

        try:
            title, lines = text.split("\n", 1)
        except ValueError:
            title = text
            lines = ""

        version, created = cls._parse_title(title)
        return cls(
            version=Version(version),
            created=created,
            text=lines,
        )

    def is_empty(self) -> bool:
        """
        Whether release has no text.
        """
        return self.body.is_empty()

    def set_section(self, title: str, text: str) -> None:
        """
        Uverwrite release section.

        Arguments:
            title -- Section title.
            text -- Section text.
        """
        old_body = self.body.clone()
        self.body.set_section(title, text)
        self._log_changes(old_body)

    def append_section(self, title: str, text: str) -> None:
        """
        Append new lines to release notes.

        Arguments:
            title -- Section title.
            text -- Section text to append.
        """
        new_record = RecordBody(sections=[RecordSection(title, text)])
        self.merge(new_record)

    def set_body(self, text: str) -> None:
        """
        Change record body to `text`.

        Logs changes.
        """
        old_body = self.body.clone()
        self._record_body = RecordBody.parse(text)
        self._log_changes(old_body)

    def merge(self, record_body: RecordBody) -> None:
        """
        Merge `record_body` to body of the record.

        Logs changes.
        """
        old_body = self.body.clone()
        self._record_body = old_body.get_merged(record_body)
        self._log_changes(old_body)

    def _log_changes(self, old_body: RecordBody) -> None:
        for section_title in SECTION_TITLES:
            old_section = old_body.get_section(section_title)
            new_section = self.body.get_section(section_title)
            if new_section.body == old_section.body:
                continue
            if old_section.is_empty():
                if not new_section.is_empty():
                    self._logger.info(f"{self.name} `{new_section.title}` section added")
            else:
                if new_section.is_empty():
                    self._logger.info(f"{self.name} `{new_section.title}` section deleted")
                else:
                    self._logger.info(f"{self.name} `{new_section.title}` section updated")
