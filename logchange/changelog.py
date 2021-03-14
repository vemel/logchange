"""
Wrapper for full `CHANGELOG.md` content.
"""
from typing import Iterator, List, Optional, Type, TypeVar

from newversion import Version

from logchange.record import Record
from logchange.utils import dedent

_R = TypeVar("_R", bound="ChangeLog")


class ChangeLog:
    """
    Wrapper for full `CHANGELOG.md` content.

    Arguments:
        head -- Head of changelog
        released -- Released content
        unrelease -- Unreleased content
    """

    PARTS_DELIM = "\n\n"

    # Released section title in CHANGELOG.md
    RELEASED_MARKER = "## ["

    # Unreleased section title in CHANGELOG.md
    UNRELEASED_MARKER = "## [Unreleased]"

    def __init__(self, head: str, released: str, unreleased: str) -> None:
        self.head: str = head
        self._released = released.strip()
        self._released_records: List[Record] = []
        self._unreleased = Record(Version.zero(), created="", text=unreleased)

    @property
    def released(self) -> List[Record]:
        if not self._released_records:
            self._released_records = list(self.iterate_records())

        return self._released_records

    @classmethod
    def parse(cls: Type[_R], text: str) -> _R:
        """
        Parse from `CHANGELOG.md` content.

        Arguments:
            text -- CHANGELOG.md text content.
        """
        head = dedent(text)
        released = ""
        unreleased = ""

        if cls.UNRELEASED_MARKER in head:
            head, unreleased = head.split(cls.UNRELEASED_MARKER, 1)
            if cls.RELEASED_MARKER in unreleased:
                unreleased, rest = unreleased.split(cls.RELEASED_MARKER, 1)
                released = f"{cls.RELEASED_MARKER}{rest}"

        if cls.RELEASED_MARKER in head:
            head, rest = head.split(cls.RELEASED_MARKER, 1)
            released = f"{cls.RELEASED_MARKER}{rest}"

        return cls(
            head=dedent(head),
            unreleased=dedent(unreleased),
            released=dedent(released),
        )

    def _render_released(self) -> str:
        return self._released

    def render(self) -> str:
        """
        Render to string.
        """
        parts = [self.head]
        parts.append(self._unreleased.render())
        if self.released:
            parts.append(self._render_released())

        return self.PARTS_DELIM.join(parts).strip() + "\n"

    def get_latest(self) -> Optional[Record]:
        """
        Get latest release record.

        Returns:
            Release record or None.
        """
        for record in self.iterate_records():
            return record

        return None

    def get_unreleased(self) -> Record:
        """
        Get unreleased record.

        Returns:
            Release record.
        """
        return self._unreleased

    def get_record(self, version: Version) -> Optional[Record]:
        """
        Get record by release version.

        Arguments:
            version -- release version.

        Returns:
            Release record or None.
        """
        for record in self.iterate_records():
            if record.version == version:
                return record

        return None

    def iterate_records(self) -> Iterator[Record]:
        """
        Iterate over release records from newest to oldest.

        Yields:
            Release record.
        """
        for record_text in self._released.split(self.RELEASED_MARKER):
            if not record_text.strip():
                continue
            record = Record.parse(f"{self.RELEASED_MARKER}{record_text}")
            yield record

    def format_released(self) -> None:
        """
        Format all released records.
        """
        record_rendered = []
        for record in self.released:
            record_rendered.append(record.render())

        self._released = "\n\n".join(record_rendered)

    def add_release(self, record: Record) -> None:
        """
        Add new release.

        Arguments:
            record -- New release record.
        """
        if self._released:
            self._released = f"{record.render()}\n\n{self._released}"
            return

        self._released = record.render()

    def update_release(self, record: Record) -> None:
        """
        Add or update release `record`.

        Arguments:
            record -- Record to update.
        """
        if record.version == Version.zero():
            self._unreleased.body = record.body
            return

        for old_record in self.released:
            if record.version == old_record.version:
                old_record.body = record.body
                old_record.created = record.created
                self.format_released()
                return

        self.add_release(record)
