from typing import Dict, Iterable, Iterator, Type, TypeVar

from newversion import Version

from logchange.constants import MAJOR_SECTION_TITLES, MINOR_SECTION_TITLES, SECTION_TITLES
from logchange.record_section import RecordSection
from logchange.utils import dedent

_R = TypeVar("_R", bound="RecordBody")


class RecordBody:
    """
    Keep a changelog release body.
    """

    PARTS_DELIM = "\n\n"

    def __init__(
        self,
        sections: Iterable[RecordSection] = (),
        prefix: str = "",
        postfix: str = "",
    ) -> None:
        self._sections: Dict[str, RecordSection] = {i: RecordSection(i, "") for i in SECTION_TITLES}
        self.prefix: str = prefix
        self.postfix: str = postfix
        for section in sections:
            self.append_lines(section.title, section.body)

    @property
    def sections(self) -> Iterator[RecordSection]:
        """
        Iterate over non-empty sections.

        Yields:
            RecordSection.
        """
        for section in self._sections.values():
            if section.is_empty():
                continue
            yield section

    def bump_version(self, old_version: Version) -> Version:
        """
        Bump version based on present changelog sections.
        """
        for major_title in MAJOR_SECTION_TITLES:
            section = self.get_section(major_title)
            if section and not section.is_empty():
                return old_version.bump_major()

        for major_title in MINOR_SECTION_TITLES:
            section = self.get_section(major_title)
            if section and not section.is_empty():
                return old_version.bump_minor()

        return old_version.bump_micro()

    def bump_rc_version(self, old_version: Version) -> Version:
        """
        Bump ReleaseCandidate version.
        """
        new_version = self.bump_version(old_version)
        if old_version.get_stable() == new_version:
            return old_version.bump_prerelease()

        return new_version.replace(rc=1)

    def get_section(self, title: str) -> RecordSection:
        """
        Get section by `title`.

        Arguments:
            title -- Section title.

        Returns:
            Found Record Section.
        """
        title = title.lower()
        if title not in self._sections:
            raise ValueError(f"Invalid section title: {title}")

        return self._sections[title.lower()]

    def render(self) -> str:
        """
        Render to string.
        """
        parts = []

        if self.prefix:
            parts.append(self.prefix)

        for section_title in SECTION_TITLES:
            section = self.get_section(section_title)
            if section.is_empty():
                continue
            parts.append(section.render())

        if self.postfix:
            parts.append(self.postfix)

        parts = [i for i in parts if i]
        return self.PARTS_DELIM.join(parts)

    def set_section(self, title: str, body: str) -> None:
        """
        Change section `title` text content to `body`.
        """
        self.get_section(title).body = body

    def append_lines(self, title: str, text: str) -> None:
        """
        Append text after new line to `title` section.

        Arguments:
            title -- Section title.
            text -- Text to append.
        """
        self.get_section(title).append_lines(text)

    def append_to_all(self, text: str) -> None:
        """
        Append `text` to all non-empty sections.
        """
        for section in self.sections:
            section.append(text)

    def get_merged(self: _R, other: _R) -> _R:
        """
        Create a new body from current and `other`.

        Arguments:
            other -- Other record body.

        Returns:
            New RecordBody.
        """
        result = self.__class__()
        for section_title in SECTION_TITLES:
            old_section = self.get_section(section_title)
            new_section = other.get_section(section_title)
            result.append_lines(section_title, old_section.body)
            result.append_lines(section_title, new_section.body)

        return result

    @staticmethod
    def _parse_prefix_section(line: str) -> str:
        if ":" not in line:
            return ""

        line_lower = line.lower()
        for section_title in SECTION_TITLES:
            if line_lower.startswith(f"{section_title}:"):
                return section_title

        return ""

    @staticmethod
    def _parse_header_title(line: str) -> str:
        if line.startswith("#") and " " in line:
            title = line.split()[1].lower()
            if title in SECTION_TITLES:
                return title
        return ""

    @staticmethod
    def _has_header(line: str) -> bool:
        return line.startswith("#") and " " in line

    @classmethod
    def parse(cls: Type[_R], text: str) -> _R:
        """
        Parse RecordBoyd from `text`.
        """
        text = dedent(text)
        title = ""
        prefix_lines = []
        postfix_lines = []
        codeblock = False
        result = cls()
        for line in text.splitlines():
            if line.startswith("```"):
                codeblock = not codeblock
            if not codeblock:
                if cls._has_header(line):
                    title = cls._parse_header_title(line)
                    if title:
                        continue

                prefix_title = cls._parse_prefix_section(line)
                if prefix_title:
                    result.append_lines(prefix_title, line[len(prefix_title) + 1 :].strip())
                    continue

            if title:
                result.append_lines(title, line)
            else:
                if result.is_empty():
                    prefix_lines.append(line)
                else:
                    postfix_lines.append(line)

        result.prefix = dedent("\n".join(prefix_lines))
        result.postfix = dedent("\n".join(postfix_lines))
        return result

    def is_empty(self) -> bool:
        """
        Whether body has no text.
        """
        if self.prefix or self.postfix:
            return False

        for _ in self.sections:
            return False

        return True

    def sanitize(self) -> None:
        """
        Remove prefix and postfix.
        """
        self.prefix = ""
        self.postfix = ""

    def clone(self: _R) -> _R:
        """
        Get a copy of record body.
        """
        return self.__class__(
            prefix=self.prefix, postfix=self.postfix, sections=(i for i in self.sections)
        )

    def clear(self) -> None:
        """
        Remove all text from record body.
        """
        self.sanitize()
        for section in self.sections:
            section.body = ""
